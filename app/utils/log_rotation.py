"""
Sistema de Log Rotation para UniFi Collector Monitor v3.0

Previne crescimento excessivo do arquivo de log do sistema de bloqueio.

Estratégia:
- Rotação por tamanho: Quando ultrapassar 5 MB
- Rotação por tempo: Diariamente
- Backup: Mantém últimos 7 dias
- Compressão: Logs antigos são comprimidos (.gz)
- Limpeza: Logs com mais de 30 dias são deletados
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
import logging
from pathlib import Path


class LogRotationManager:
    """Gerenciador de rotação de logs"""
    
    def __init__(
        self,
        log_file="monitor_bloqueio_coletores.log",
        max_size_mb=5,
        backup_count=7,
        retention_days=30
    ):
        """
        Inicializa gerenciador de rotação de logs
        
        Args:
            log_file: Nome do arquivo de log principal
            max_size_mb: Tamanho máximo em MB antes de rotacionar
            backup_count: Número de backups a manter
            retention_days: Dias para manter logs antigos
        """
        self.log_file = Path(log_file)
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Converte para bytes
        self.backup_count = backup_count
        self.retention_days = retention_days
    
    def should_rotate(self):
        """Verifica se deve rotacionar o log"""
        if not self.log_file.exists():
            return False
        
        # Verifica tamanho
        size = self.log_file.stat().st_size
        if size >= self.max_size_bytes:
            return True
        
        # Verifica idade (rotação diária)
        mod_time = datetime.fromtimestamp(self.log_file.stat().st_mtime)
        age = datetime.now() - mod_time
        if age.days >= 1:
            return True
        
        return False
    
    def rotate(self):
        """Executa rotação do log"""
        if not self.log_file.exists():
            return
        
        try:
            # Gerar nome do backup com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{self.log_file.stem}_{timestamp}.log"
            backup_path = self.log_file.parent / backup_name
            
            # Mover arquivo atual para backup
            shutil.move(str(self.log_file), str(backup_path))
            
            # Comprimir backup após rotação
            self._compress_backup(backup_path)
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            logging.info(f"[LOG ROTATION] Arquivo rotacionado: {backup_name}")
            
        except Exception as e:
            logging.error(f"[LOG ROTATION] Erro ao rotacionar: {e}")
    
    def _compress_backup(self, backup_path):
        """Comprime arquivo de backup"""
        try:
            compressed_path = Path(str(backup_path) + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove arquivo original após compressão
            backup_path.unlink()
            
            logging.info(f"[LOG ROTATION] Backup comprimido: {compressed_path.name}")
            
        except Exception as e:
            logging.error(f"[LOG ROTATION] Erro ao comprimir: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado em retention_days"""
        try:
            pattern = f"{self.log_file.stem}_*.log.gz"
            log_dir = self.log_file.parent
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            deleted_count = 0
            for backup_file in log_dir.glob(pattern):
                # Extrai timestamp do nome do arquivo
                try:
                    timestamp_str = backup_file.stem.split('_')[-2:]
                    timestamp_str = '_'.join(timestamp_str).replace('.log', '')
                    file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    
                    # Remove se for mais antigo que retention_days
                    if file_date < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        logging.info(f"[LOG ROTATION] Backup antigo removido: {backup_file.name}")
                
                except (ValueError, IndexError):
                    # Ignora arquivos com formato de nome incorreto
                    continue
            
            if deleted_count > 0:
                logging.info(f"[LOG ROTATION] Total de backups removidos: {deleted_count}")
        
        except Exception as e:
            logging.error(f"[LOG ROTATION] Erro ao limpar backups: {e}")
    
    def get_log_stats(self):
        """Retorna estatísticas dos logs"""
        stats = {
            'current_size_mb': 0,
            'backup_count': 0,
            'total_size_mb': 0,
            'oldest_backup': None,
            'newest_backup': None
        }
        
        try:
            # Tamanho do arquivo atual
            if self.log_file.exists():
                stats['current_size_mb'] = round(
                    self.log_file.stat().st_size / (1024 * 1024), 2
                )
            
            # Backups
            pattern = f"{self.log_file.stem}_*.log.gz"
            log_dir = self.log_file.parent
            backups = list(log_dir.glob(pattern))
            
            stats['backup_count'] = len(backups)
            
            if backups:
                # Tamanho total
                total_bytes = sum(b.stat().st_size for b in backups)
                stats['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)
                
                # Mais antigo e mais novo
                dates = []
                for backup in backups:
                    try:
                        timestamp_str = backup.stem.split('_')[-2:]
                        timestamp_str = '_'.join(timestamp_str).replace('.log', '')
                        file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        dates.append(file_date)
                    except:
                        continue
                
                if dates:
                    stats['oldest_backup'] = min(dates).strftime('%d/%m/%Y %H:%M')
                    stats['newest_backup'] = max(dates).strftime('%d/%m/%Y %H:%M')
        
        except Exception as e:
            logging.error(f"[LOG ROTATION] Erro ao obter estatísticas: {e}")
        
        return stats


def setup_rotating_logger(
    name,
    log_file="monitor_bloqueio_coletores.log",
    level=logging.INFO,
    max_size_mb=5,
    backup_count=7
):
    """
    Configura logger com rotação automática
    
    Args:
        name: Nome do logger
        log_file: Arquivo de log
        level: Nível de log (INFO, WARNING, ERROR)
        max_size_mb: Tamanho máximo antes de rotacionar
        backup_count: Número de backups a manter
    
    Returns:
        Tuple (logger, rotation_manager)
    """
    # Criar gerenciador de rotação
    rotation_manager = LogRotationManager(
        log_file=log_file,
        max_size_mb=max_size_mb,
        backup_count=backup_count
    )
    
    # Verificar se deve rotacionar antes de iniciar
    if rotation_manager.should_rotate():
        rotation_manager.rotate()
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remover handlers existentes
    logger.handlers.clear()
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger, rotation_manager


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logger com rotação
    logger, rotation_manager = setup_rotating_logger(
        name='test_rotation',
        log_file='monitor_bloqueio_coletores.log',
        max_size_mb=5,
        backup_count=7
    )
    
    # Usar logger normalmente
    logger.info("Sistema iniciado")
    
    # Verificar estatísticas
    stats = rotation_manager.get_log_stats()
    print(f"Estatísticas de Logs:")
    print(f"  Arquivo atual: {stats['current_size_mb']} MB")
    print(f"  Backups: {stats['backup_count']}")
    print(f"  Tamanho total backups: {stats['total_size_mb']} MB")
    
    # Rotacionar manualmente se necessário
    if rotation_manager.should_rotate():
        logger.info("Rotacionando log...")
        rotation_manager.rotate()