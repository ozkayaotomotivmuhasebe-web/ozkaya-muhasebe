"""
Google Sheets Entegrasyon Servisi
Google Sheets'ten veri çekip veritabanına aktarır
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import gspread
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from src.database.db import session_scope
from src.database.models import Transaction, Cari, BankAccount, CreditCard, Loan, TransactionType, PaymentMethod
from src.services.user_settings_service import UserSettingsService
from src.services.transaction_service import TransactionService
from config import PROJECT_ROOT

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Google Sheets ile senkronizasyon servisi (Çift yönlü - okuma ve yazma)"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # Okuma ve yazma izni
    CREDENTIALS_DIR = PROJECT_ROOT / "data" / "google_credentials"
    TOKEN_FILE = CREDENTIALS_DIR / "token.json"
    CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
    
    def __init__(self):
        self.CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        self.client = None
        self.last_sync = None

    def _resolve_credentials_file(self) -> Path:
        """credentials.json için olası yolları sırayla kontrol et"""
        candidates = [
            self.CREDENTIALS_FILE,
            PROJECT_ROOT.parent / "data" / "google_credentials" / "credentials.json",
            Path.cwd() / "data" / "google_credentials" / "credentials.json",
            Path(sys.executable).parent / "data" / "google_credentials" / "credentials.json",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return self.CREDENTIALS_FILE
    
    def authenticate(self) -> Tuple[bool, str]:
        """
        Google Sheets için kimlik doğrulama
        Returns: (başarılı mı, mesaj)
        """
        try:
            creds = None
            credentials_file = self._resolve_credentials_file()
            token_file = credentials_file.parent / "token.json"
            token_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Eğer token varsa yükle
            if token_file.exists():
                with open(token_file, 'r') as token:
                    creds = Credentials.from_authorized_user_info(json.load(token), self.SCOPES)
            
            # Token yoksa veya geçersizse yenile
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        logger.warning(f"Token yenileme hatası: {e}")
                        creds = None
                
                if not creds:
                    # Credentials dosyası yoksa hata ver
                    if not credentials_file.exists():
                        return False, "credentials.json dosyası bulunamadı. Lütfen Google Cloud Console'dan indirip data/google_credentials klasörüne koyun."
                    
                    # OAuth2 flow başlat
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_file), self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Token'ı kaydet
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # gspread client oluştur
            self.client = gspread.authorize(creds)
            return True, "Google Sheets bağlantısı başarılı!"
            
        except Exception as e:
            logger.error(f"Google Sheets kimlik doğrulama hatası: {e}")
            return False, f"Kimlik doğrulama hatası: {str(e)}"
    
    def test_connection(self, spreadsheet_id: str) -> Tuple[bool, str]:
        """
        Belirtilen Google Sheets'e erişimi test et
        """
        try:
            if not self.client:
                success, msg = self.authenticate()
                if not success:
                    return False, msg
            
            sheet = self.client.open_by_key(spreadsheet_id)
            return True, f"Bağlantı başarılı! Sayfa adı: {sheet.title}"
            
        except gspread.exceptions.SpreadsheetNotFound:
            return False, "Spreadsheet bulunamadı. ID'yi kontrol edin ve sayfanın paylaşıldığından emin olun."
        except Exception as e:
            logger.error(f"Bağlantı test hatası: {e}")
            return False, f"Bağlantı hatası: {str(e)}"
    
    def sync_from_sheets(self, user_id: int, spreadsheet_id: str, sheet_mappings: Dict[str, str]) -> Tuple[bool, str, Dict]:
        """
        Google Sheets'ten veri çek ve veritabanına aktar
        
        Args:
            user_id: Kullanıcı ID
            spreadsheet_id: Google Sheets ID
            sheet_mappings: Sayfa isimleri mapping'i (örn: {'transactions': 'İşlemler', 'caris': 'Cariler', ...})
        
        Returns:
            (başarılı mı, mesaj, istatistikler)
        """
        try:
            if not self.client:
                success, msg = self.authenticate()
                if not success:
                    return False, msg, {}

            spreadsheet = self.client.open_by_key(spreadsheet_id)
            stats = {
                'transactions_added': 0,
                'transactions_updated': 0,
                'caris_added': 0,
                'gelen_fatura_added': 0,
                'kesilen_fatura_added': 0,
                'gider_added': 0,
                'gelir_added': 0,
                'errors': []
            }

            # Cari hesapları senkronize et (önce bunlar olmalı)
            if 'caris' in sheet_mappings:
                try:
                    worksheet = spreadsheet.worksheet(sheet_mappings['caris'])
                    cari_stats = self._sync_caris(user_id, worksheet)
                    stats['caris_added'] = cari_stats['added']
                except gspread.exceptions.WorksheetNotFound:
                    stats['errors'].append(f"'{sheet_mappings['caris']}' sayfası bulunamadı")

            # İşlemleri senkronize et (ana işlemler sayfası)
            if 'transactions' in sheet_mappings:
                try:
                    worksheet = spreadsheet.worksheet(sheet_mappings['transactions'])
                    trans_stats = self._sync_transactions(user_id, worksheet)
                    stats['transactions_added'] = trans_stats['added']
                    stats['transactions_updated'] = trans_stats['updated']
                except gspread.exceptions.WorksheetNotFound:
                    stats['errors'].append(f"'{sheet_mappings['transactions']}' sayfası bulunamadı")

            # Ekstra sayfalar: Gelen Fatura, Kesilen Fatura, Gider, Gelir
            extra_sheets = [
                ('gelen_fatura', 'gelen_fatura_added', TransactionType.GELEN_FATURA),
                ('kesilen_fatura', 'kesilen_fatura_added', TransactionType.KESILEN_FATURA),
                ('gider', 'gider_added', TransactionType.GIDER),
                ('gelir', 'gelir_added', TransactionType.GELIR)
            ]
            for key, stat_key, forced_type in extra_sheets:
                if key in sheet_mappings:
                    try:
                        worksheet = spreadsheet.worksheet(sheet_mappings[key])
                        # Bu sayfalardaki verileri işlemler tablosuna ekle, türü zorla
                        trans_stats = self._sync_transactions(user_id, worksheet, override_type=forced_type)
                        stats[stat_key] = trans_stats['added']
                        stats['transactions_added'] += trans_stats['added']
                        stats['transactions_updated'] += trans_stats['updated']
                    except gspread.exceptions.WorksheetNotFound:
                        stats['errors'].append(f"'{sheet_mappings[key]}' sayfası bulunamadı")

            # Son senkronizasyon zamanını kaydet
            self.last_sync = datetime.now()
            UserSettingsService.set_setting(user_id, 'google_sheets_last_sync', self.last_sync.isoformat())

            msg = f"Senkronizasyon tamamlandı! Yeni cari: {stats['caris_added']}, Yeni işlem: {stats['transactions_added']}"
            if stats['gelen_fatura_added']:
                msg += f", Gelen Fatura: {stats['gelen_fatura_added']}"
            if stats['kesilen_fatura_added']:
                msg += f", Kesilen Fatura: {stats['kesilen_fatura_added']}"
            if stats['gider_added']:
                msg += f", Gider: {stats['gider_added']}"
            if stats['gelir_added']:
                msg += f", Gelir: {stats['gelir_added']}"
            if stats['errors']:
                msg += f"\n⚠️ Uyarılar: {', '.join(stats['errors'])}"

            return True, msg, stats

        except Exception as e:
            logger.error(f"Senkronizasyon hatası: {e}", exc_info=True)
            return False, f"Senkronizasyon hatası: {str(e)}", {}
    
    def _sync_caris(self, user_id: int, worksheet) -> Dict:
        """Cari hesapları Google Sheets'ten çek"""
        stats = {'added': 0, 'skipped': 0}
        
        try:
            # İlk satır başlık, veriyi al
            all_values = worksheet.get_all_values()
            if len(all_values) < 2:
                return stats
            
            headers = all_values[0]
            rows = all_values[1:]
            
            # Sütun indekslerini bul (flexible)
            col_map = {}
            for i, header in enumerate(headers):
                h = header.lower().strip()
                if 'ad' in h or 'isim' in h or 'ünvan' in h:
                    col_map['name'] = i
                elif 'tip' in h or 'tür' in h:
                    col_map['type'] = i
                elif 'telefon' in h or 'tel' in h:
                    col_map['phone'] = i
                elif 'adres' in h:
                    col_map['address'] = i
                elif 'vergi' in h or 'tc' in h:
                    col_map['tax_no'] = i
            
            if 'name' not in col_map:
                logger.warning("Cari sayfasında 'Ad' sütunu bulunamadı")
                return stats
            
            with session_scope() as session:
                for row in rows:
                    if len(row) <= col_map['name'] or not row[col_map['name']].strip():
                        continue
                    
                    name = row[col_map['name']].strip()
                    
                    # Bu cari zaten var mı kontrol et
                    existing = session.query(Cari).filter_by(user_id=user_id, name=name).first()
                    if existing:
                        stats['skipped'] += 1
                        continue
                    
                    # Yeni cari oluştur
                    cari_type = 'MÜŞTERİ'
                    if 'type' in col_map and len(row) > col_map['type']:
                        type_val = row[col_map['type']].strip().upper()
                        if 'TEDARİK' in type_val or 'SATIŞ' in type_val:
                            cari_type = 'TEDARİKÇİ'
                    
                    new_cari = Cari(
                        user_id=user_id,
                        name=name,
                        cari_type=cari_type,
                        phone=row[col_map['phone']].strip() if 'phone' in col_map and len(row) > col_map['phone'] else None,
                        address=row[col_map['address']].strip() if 'address' in col_map and len(row) > col_map['address'] else None,
                        tax_number=row[col_map['tax_no']].strip() if 'tax_no' in col_map and len(row) > col_map['tax_no'] else None
                    )
                    session.add(new_cari)
                    stats['added'] += 1
            
            logger.info(f"Cari senkronizasyonu: {stats['added']} eklendi, {stats['skipped']} atlandı")
            
        except Exception as e:
            logger.error(f"Cari senkronizasyon hatası: {e}", exc_info=True)
        
        return stats
    
    def _sync_transactions(self, user_id: int, worksheet, override_type=None) -> Dict:
        """İşlemleri Google Sheets'ten çek"""
        stats = {
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'duplicates': 0,
            'duplicate_transactions': []
        }
        
        try:
            all_values = worksheet.get_all_values()
            if len(all_values) < 2:
                return stats
            
            headers = all_values[0]
            rows = all_values[1:]
            
            # Sütun indekslerini bul
            col_map = {}
            for i, header in enumerate(headers):
                h = header.lower().strip()
                if 'tarih' in h or 'date' in h:
                    col_map['date'] = i
                elif 'tür' in h or 'tip' in h or 'type' in h:
                    col_map['type'] = i
                elif 'tutar' in h or 'miktar' in h or 'amount' in h:
                    col_map['amount'] = i
                elif 'açıklama' in h or 'description' in h:
                    col_map['description'] = i
                elif 'konu' in h or 'subject' in h:
                    col_map['subject'] = i
                elif 'ödeyen' in h or 'person' in h:
                    col_map['person'] = i
                elif 'cari' in h or 'müşteri' in h or 'ünvan' in h or 'customer' in h:
                    col_map['cari'] = i
                # Ödeme şekli kolonunu daha öncelikli kontrol et
                elif 'şekil' in h or ('yöntem' in h and 'ödeme' in h):
                    col_map['payment_type'] = i
                elif 'ödeme' in h or 'payment' in h:
                    col_map['payment'] = i
            
            logger.info(f"Kolon eşleştirmeleri: {col_map}")
            
            if 'date' not in col_map or 'amount' not in col_map:
                logger.warning("İşlem sayfasında 'Tarih' veya 'Tutar' sütunu bulunamadı")
                return stats
            
            with session_scope() as session:
                for row_idx, row in enumerate(rows, start=2):
                    if len(row) <= col_map['amount'] or not row[col_map['amount']].strip():
                        continue
                    
                    try:
                        # Tarihi parse et
                        date_str = row[col_map['date']].strip()
                        # Farklı tarih formatlarını dene
                        for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                            try:
                                trans_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            logger.warning(f"Tarih formatı tanınmıyor: {date_str}")
                            continue
                        
                        # Tutarı parse et - Türkçe format destekle (1.234,56 veya 1.234.567 veya 1234.56)
                        amount_str = row[col_map['amount']].strip().replace('\xa0', '').replace('₺', '').replace('TL', '').replace(' ', '')
                        if ',' in amount_str:
                            # Türkçe format: binlik nokta, ondalık virgül → 1.234,56
                            amount_str = amount_str.replace('.', '').replace(',', '.')
                        elif amount_str.count('.') > 1:
                            # Birden fazla nokta = binlik ayırıcı → 1.234.567
                            amount_str = amount_str.replace('.', '')
                        amount = float(amount_str)
                        
                        # İşlem türü
                        if override_type is not None:
                            trans_type = override_type
                        else:
                            trans_type = TransactionType.GELIR
                            if 'type' in col_map and len(row) > col_map['type']:
                                type_str = row[col_map['type']].strip().upper()
                                if 'GİDER' in type_str or 'EXPENSE' in type_str:
                                    trans_type = TransactionType.GIDER
                                elif 'FATURA' in type_str:
                                    trans_type = TransactionType.KESILEN_FATURA if amount > 0 else TransactionType.GELEN_FATURA
                        
                        # Cari bul
                        cari_id = None
                        customer_name = ""
                        if 'cari' in col_map and len(row) > col_map['cari']:
                            cari_name = row[col_map['cari']].strip()
                            if cari_name:
                                cari = session.query(Cari).filter_by(user_id=user_id, name=cari_name).first()
                                if not cari:
                                    # CariService ile ekle
                                    from src.services.cari_service import CariService
                                    ok, _ = CariService.create_cari(user_id, cari_name, "MÜŞTERİ")
                                    if ok:
                                        cari = session.query(Cari).filter_by(user_id=user_id, name=cari_name).first()
                                if cari:
                                    cari_id = cari.id
                                customer_name = cari_name
                        
                        # Açıklama
                        description = row[col_map['description']].strip() if 'description' in col_map and len(row) > col_map['description'] else ''
                        
                        # Konu
                        subject = row[col_map['subject']].strip() if 'subject' in col_map and len(row) > col_map['subject'] else None
                        
                        # Ödeyen Kişi
                        person = row[col_map['person']].strip() if 'person' in col_map and len(row) > col_map['person'] else None
                        
                        # Ödeme Şekli (payment_type - string)
                        payment_type = row[col_map['payment_type']].strip() if 'payment_type' in col_map and len(row) > col_map['payment_type'] else None
                        logger.info(f"Satır {row_idx}: payment_type = '{payment_type}'")
                        
                        # Ödeme yöntemi ve hesap bilgilerini belirle
                        payment_method = PaymentMethod.NAKIT
                        bank_account_id = None
                        credit_card_id = None
                        
                        if payment_type:
                            payment_type_upper = payment_type.upper()
                            
                            # NAKİT kontrolü
                            if 'NAKİT' in payment_type_upper or 'NAKIT' in payment_type_upper or 'CASH' in payment_type_upper:
                                payment_method = PaymentMethod.NAKIT
                            
                            # CARİ kontrolü
                            elif 'CARİ' in payment_type_upper or 'CARI' in payment_type_upper:
                                payment_method = PaymentMethod.CARI
                            
                            # Diğer durumda hesap numarası/adı olabilir - banka hesabı ara
                            else:
                                # Önce banka hesaplarında ara
                                bank_account = session.query(BankAccount).filter(
                                    BankAccount.user_id == user_id,
                                    BankAccount.is_active == True
                                ).filter(
                                    (BankAccount.account_number.ilike(f'%{payment_type}%')) |
                                    (BankAccount.bank_name.ilike(f'%{payment_type}%')) |
                                    (BankAccount.iban.ilike(f'%{payment_type}%'))
                                ).first()
                                
                                if bank_account:
                                    payment_method = PaymentMethod.BANKA
                                    bank_account_id = bank_account.id
                                else:
                                    # Bulunamazsa kredi kartlarında ara
                                    credit_card = session.query(CreditCard).filter(
                                        CreditCard.user_id == user_id,
                                        CreditCard.is_active == True
                                    ).filter(
                                        (CreditCard.card_name.ilike(f'%{payment_type}%')) |
                                        (CreditCard.card_number_last4.ilike(f'%{payment_type}%')) |
                                        (CreditCard.bank_name.ilike(f'%{payment_type}%'))
                                    ).first()
                                    
                                    if credit_card:
                                        payment_method = PaymentMethod.KREDI_KARTI
                                        credit_card_id = credit_card.id
                                    else:
                                        # Hiçbiri bulunmazsa varsayılan olarak BANKA
                                        payment_method = PaymentMethod.BANKA
                        
                        # Aynı işlem var mı kontrol et (tarih + tutar + açıklama)
                        existing = TransactionService.find_duplicate_transaction(
                            user_id,
                            trans_date,
                            amount,
                            description,
                            customer_name=customer_name,
                            person=person
                        )

                        if existing:
                            stats['skipped'] += 1
                            stats['duplicates'] += 1
                            stats['duplicate_transactions'].append({
                                'row_key': row_idx,
                                'row_label': str(row_idx),
                                'date': trans_date,
                                'customer_name': customer_name,
                                'amount': amount,
                                'description': description,
                                'subject': subject,
                                'person': person,
                                'transaction_type': trans_type,
                                'payment_method': payment_method,
                                'cari_id': cari_id,
                                'payment_type': payment_type or payment_method.value
                            })
                            continue
                        
                        # Yeni işlem oluştur
                        new_transaction = Transaction(
                            user_id=user_id,
                            transaction_type=trans_type,
                            amount=amount,
                            transaction_date=trans_date,
                            description=description,
                            subject=subject,
                            person=person,
                            customer_name=customer_name,
                            payment_method=payment_method,
                            cari_id=cari_id,
                            bank_account_id=bank_account_id,
                            credit_card_id=credit_card_id,
                            payment_type=payment_type or payment_method.value
                        )
                        session.add(new_transaction)
                        stats['added'] += 1
                        
                    except Exception as e:
                        logger.warning(f"Satır parse hatası: {e}, satır: {row}")
                        continue
            
            logger.info(f"İşlem senkronizasyonu: {stats['added']} eklendi, {stats['skipped']} atlandı")
            
        except Exception as e:
            logger.error(f"İşlem senkronizasyon hatası: {e}", exc_info=True)
        
        return stats

    def sync_to_sheets(self, user_id: int, spreadsheet_id: str, sheet_mappings: Dict[str, str]) -> Tuple[bool, str, Dict]:
        """Uygulamadaki verileri Google Sheets'e yaz"""
        try:
            if not self.client:
                success, msg = self.authenticate()
                if not success:
                    return False, msg, {}

            spreadsheet = self.client.open_by_key(spreadsheet_id)
            stats = {
                'caris_pushed': 0,
                'transactions_pushed': 0,
                'errors': []
            }

            if 'caris' in sheet_mappings:
                try:
                    worksheet = self._get_or_create_worksheet(spreadsheet, sheet_mappings['caris'])
                    stats['caris_pushed'] = self._push_caris_to_sheet(user_id, worksheet)
                except Exception as e:
                    stats['errors'].append(f"Cari yazma hatası: {str(e)}")

            if 'transactions' in sheet_mappings:
                try:
                    worksheet = self._get_or_create_worksheet(spreadsheet, sheet_mappings['transactions'])
                    stats['transactions_pushed'] = self._push_transactions_to_sheet(user_id, worksheet)
                except Exception as e:
                    stats['errors'].append(f"İşlem yazma hatası: {str(e)}")

            msg = f"Sheets'e yazma tamamlandı! Cari: {stats['caris_pushed']}, İşlem: {stats['transactions_pushed']}"
            if stats['errors']:
                msg += f"\n⚠️ Uyarılar: {', '.join(stats['errors'])}"

            return True, msg, stats

        except Exception as e:
            logger.error(f"Sheets'e yazma hatası: {e}", exc_info=True)
            return False, f"Sheets'e yazma hatası: {str(e)}", {}

    def sync_bidirectional(self, user_id: int, spreadsheet_id: str, sheet_mappings: Dict[str, str]) -> Tuple[bool, str, Dict]:
        """Çift yönlü senkronizasyon (Sheets -> App ve App -> Sheets)"""
        try:
            pull_success, pull_message, pull_stats = self.sync_from_sheets(user_id, spreadsheet_id, sheet_mappings)
            if not pull_success:
                return False, pull_message, {}

            push_success, push_message, push_stats = self.sync_to_sheets(user_id, spreadsheet_id, sheet_mappings)
            if not push_success:
                return False, push_message, {}

            merged_stats = {
                **pull_stats,
                **push_stats
            }

            message = (
                "Çift yönlü senkronizasyon tamamlandı!\n"
                f"Sheets -> Uygulama: Yeni cari {pull_stats.get('caris_added', 0)}, Yeni işlem {pull_stats.get('transactions_added', 0)}\n"
                f"Uygulama -> Sheets: Cari {push_stats.get('caris_pushed', 0)}, İşlem {push_stats.get('transactions_pushed', 0)}"
            )

            return True, message, merged_stats

        except Exception as e:
            logger.error(f"Çift yönlü senkronizasyon hatası: {e}", exc_info=True)
            return False, f"Çift yönlü senkronizasyon hatası: {str(e)}", {}

    def _get_or_create_worksheet(self, spreadsheet, sheet_name: str):
        """Worksheet'i getir, yoksa oluştur"""
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)

    def _push_caris_to_sheet(self, user_id: int, worksheet) -> int:
        """DB'deki carileri sheet'e ekle (sadece eksikler)"""
        default_headers = ["Ad/Ünvan", "Tür", "Telefon", "Adres", "Vergi No"]
        all_values = worksheet.get_all_values()
        if not all_values:
            worksheet.append_row(default_headers)
            all_values = [default_headers]

        headers = all_values[0]
        col_map = {h.lower().strip(): i for i, h in enumerate(headers)}
        name_idx = col_map.get('ad/ünvan', col_map.get('ad', col_map.get('ünvan', 0)))

        existing_names = set()
        for row in all_values[1:]:
            if len(row) > name_idx and row[name_idx].strip():
                existing_names.add(row[name_idx].strip().lower())

        added_count = 0
        rows_to_add = []

        with session_scope() as session:
            caris = session.query(Cari).filter(Cari.user_id == user_id).order_by(Cari.id.asc()).all()
            for cari in caris:
                key = (cari.name or '').strip().lower()
                if not key or key in existing_names:
                    continue

                rows_to_add.append([
                    cari.name or '',
                    cari.cari_type or '',
                    cari.phone or '',
                    cari.address or '',
                    cari.tax_number or ''
                ])
                existing_names.add(key)
                added_count += 1

        if rows_to_add:
            worksheet.append_rows(rows_to_add, value_input_option='USER_ENTERED')

        return added_count

    def _push_transactions_to_sheet(self, user_id: int, worksheet) -> int:
        """DB'deki işlemleri sheet'e ekle (sadece eksikler)"""
        default_headers = ["Tarih", "Tür", "Tutar", "Açıklama", "Cari", "Ödeme"]
        all_values = worksheet.get_all_values()
        if not all_values:
            worksheet.append_row(default_headers)
            all_values = [default_headers]

        headers = all_values[0]
        col_map = {}
        for i, header in enumerate(headers):
            h = header.lower().strip()
            if 'tarih' in h or 'date' in h:
                col_map['date'] = i
            elif 'tür' in h or 'tip' in h or 'type' in h:
                col_map['type'] = i
            elif 'tutar' in h or 'miktar' in h or 'amount' in h:
                col_map['amount'] = i
            elif 'açıklama' in h or 'description' in h or 'konu' in h:
                col_map['description'] = i
            elif 'cari' in h or 'müşteri' in h or 'customer' in h:
                col_map['cari'] = i
            elif 'ödeme' in h or 'payment' in h:
                col_map['payment'] = i

        if 'date' not in col_map or 'amount' not in col_map:
            worksheet.clear()
            worksheet.append_row(default_headers)
            all_values = [default_headers]
            col_map = {
                'date': 0,
                'type': 1,
                'amount': 2,
                'description': 3,
                'cari': 4,
                'payment': 5
            }

        existing_keys = set()
        for row in all_values[1:]:
            key = self._build_sheet_row_key(row, col_map)
            if key:
                existing_keys.add(key)

        added_count = 0
        rows_to_add = []

        with session_scope() as session:
            transactions = session.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(Transaction.transaction_date.asc(), Transaction.id.asc()).all()

            for tx in transactions:
                date_str = tx.transaction_date.strftime('%d.%m.%Y') if tx.transaction_date else ''
                amount = float(tx.amount or 0)
                description = (tx.description or '').strip()
                cari_name = (tx.customer_name or '').strip()
                payment_value = tx.payment_method.value if tx.payment_method else (tx.payment_type or '')
                type_value = tx.transaction_type.value if tx.transaction_type else ''

                key = self._build_composite_key(date_str, amount, description, cari_name)
                if key in existing_keys:
                    continue

                rows_to_add.append([
                    date_str,
                    type_value,
                    f"{amount:.2f}",
                    description,
                    cari_name,
                    payment_value
                ])
                existing_keys.add(key)
                added_count += 1

        if rows_to_add:
            worksheet.append_rows(rows_to_add, value_input_option='USER_ENTERED')

        return added_count

    def _build_sheet_row_key(self, row: List[str], col_map: Dict[str, int]) -> Optional[str]:
        """Sheet satırından karşılaştırma anahtarı üret"""
        try:
            date_idx = col_map.get('date')
            amount_idx = col_map.get('amount')
            desc_idx = col_map.get('description')
            cari_idx = col_map.get('cari')

            if date_idx is None or amount_idx is None:
                return None
            if len(row) <= max(date_idx, amount_idx):
                return None

            date_str = row[date_idx].strip() if len(row) > date_idx else ''
            amount_str = row[amount_idx].strip() if len(row) > amount_idx else ''
            description = row[desc_idx].strip() if desc_idx is not None and len(row) > desc_idx else ''
            cari_name = row[cari_idx].strip() if cari_idx is not None and len(row) > cari_idx else ''

            if not date_str or not amount_str:
                return None

            try:
                amount = float(amount_str.replace(',', '.').replace(' ', ''))
            except ValueError:
                return None

            normalized_date = self._normalize_date_string(date_str)
            return self._build_composite_key(normalized_date, amount, description, cari_name)
        except Exception:
            return None

    def _normalize_date_string(self, date_str: str) -> str:
        """Tarihi dd.mm.yyyy formatına normalize et"""
        value = (date_str or '').strip()
        if not value:
            return ''

        for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                return datetime.strptime(value, fmt).strftime('%d.%m.%Y')
            except ValueError:
                continue

        return value

    def _build_composite_key(self, date_str: str, amount: float, description: str, cari_name: str) -> str:
        """Tekilleştirme için ortak anahtar"""
        normalized_date = self._normalize_date_string(date_str)
        normalized_amount = round(float(amount or 0), 2)
        normalized_description = (description or '').strip().lower()
        normalized_cari = (cari_name or '').strip().lower()
        return f"{normalized_date}|{normalized_amount:.2f}|{normalized_description}|{normalized_cari}"
    
    @staticmethod
    def get_spreadsheet_id_from_url(url: str) -> Optional[str]:
        """Google Sheets URL'den spreadsheet ID'yi çıkar"""
        try:
            # https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
            if '/d/' in url:
                parts = url.split('/d/')
                if len(parts) > 1:
                    spreadsheet_id = parts[1].split('/')[0]
                    return spreadsheet_id
        except Exception:
            pass
        return None
