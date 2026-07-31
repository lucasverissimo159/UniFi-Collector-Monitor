"""Data persistence manager for collaborators"""
import json
import os
from datetime import datetime, timedelta
from app.config import DATA_FILE, ARCHIVE_FOLDER, RETENTION_MONTHS, MAX_HISTORY_RECORDS

class DataManager:
    @staticmethod
    def load_data():
        """Load collaborators data from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # MIGRAÃ‡ÃƒO: Converter formato antigo para novo
                migrated = False
                for ip, collector_data in data.items():
                    if 'current' in collector_data:
                        # Se current Ã© um dict (formato antigo), converter para lista
                        if isinstance(collector_data['current'], dict):
                            if collector_data['current']:  # Se nÃ£o estÃ¡ vazio
                                collector_data['current'] = [collector_data['current']]
                            else:
                                collector_data['current'] = []
                            migrated = True
                        # Se current Ã© None, converter para lista vazia
                        elif collector_data['current'] is None:
                            collector_data['current'] = []
                            migrated = True
                
                # Se houve migraÃ§Ã£o, salvar o arquivo atualizado
                if migrated:
                    with open(DATA_FILE, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                
                return data
            except:
                return {}
        return {}
    
    @staticmethod
    def save_data(data):
        """Save collaborators data to JSON file"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    @staticmethod
    def cleanup_history_cascade(data):
        """
        Executa limpeza em cascata (3 etapas):
        1. Arquiva registros com +12 meses
        2. Remove registros com +12 meses do histÃ³rico ativo  
        3. Limita a 15 registros mais recentes
        """
        cutoff_date = datetime.now() - timedelta(days=30 * RETENTION_MONTHS)
        
        # EstatÃ­sticas
        total_archived = 0
        total_removed_by_date = 0
        total_removed_by_limit = 0
        collectors_affected = 0
        
        # Criar pasta de arquivo se nÃ£o existir
        if not os.path.exists(ARCHIVE_FOLDER):
            os.makedirs(ARCHIVE_FOLDER)
        
        # DicionÃ¡rio para arquivos por mÃªs
        archives_by_month = {}
        
        for collector_ip in data:
            history = data[collector_ip].get('history', [])
            
            if not history:
                continue
                
            old_count = len(history)
            active_history = []
            collector_changed = False
            
            # ETAPA 1 + 2: Arquivar E Remover registros antigos (>12 meses)
            for record in history:
                end_date_str = record.get('end_date', '')
                try:
                    end_date = datetime.strptime(end_date_str, '%d/%m/%Y %H:%M')
                    
                    if end_date < cutoff_date:
                        # ETAPA 1: Arquivar
                        month_key = end_date.strftime('%Y-%m')
                        if month_key not in archives_by_month:
                            archives_by_month[month_key] = []
                        
                        record['archived_from_collector'] = collector_ip
                        record['archived_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                        archives_by_month[month_key].append(record)
                        total_archived += 1
                        
                        # ETAPA 2: Remove do histÃ³rico ativo (jÃ¡ arquivado)
                        total_removed_by_date += 1
                        collector_changed = True
                    else:
                        # MantÃ©m no histÃ³rico ativo (< 12 meses)
                        active_history.append(record)
                except:
                    # Se nÃ£o conseguir parsear, mantÃ©m
                    active_history.append(record)
            
            # ETAPA 3: Limitar a MAX_HISTORY_RECORDS mais recentes
            if len(active_history) > MAX_HISTORY_RECORDS:
                removed_count = len(active_history) - MAX_HISTORY_RECORDS
                # MantÃ©m apenas os Ãºltimos MAX_HISTORY_RECORDS
                active_history = active_history[-MAX_HISTORY_RECORDS:]
                total_removed_by_limit += removed_count
                collector_changed = True
            
            # Atualizar histÃ³rico se houve mudanÃ§as
            if collector_changed:
                data[collector_ip]['history'] = active_history
                collectors_affected += 1
        
        # Salvar arquivos de arquivo
        archive_files_created = 0
        for month_key, records in archives_by_month.items():
            archive_file = os.path.join(ARCHIVE_FOLDER, f"historico_{month_key}.json")
            
            # Se arquivo existe, mesclar
            existing_records = []
            if os.path.exists(archive_file):
                try:
                    with open(archive_file, 'r', encoding='utf-8') as f:
                        existing_records = json.load(f)
                except:
                    existing_records = []
            
            existing_records.extend(records)
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(existing_records, f, indent=4, ensure_ascii=False)
            
            archive_files_created += 1
        
        return {
            'archived': total_archived,
            'removed_by_date': total_removed_by_date,
            'removed_by_limit': total_removed_by_limit,
            'collectors_affected': collectors_affected,
            'archive_files': archive_files_created,
            'data': data
        }