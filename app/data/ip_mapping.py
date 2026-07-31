"""
Sistema Inteligente de Mapeamento entre Número de Coletor e IP
Suporta dois modos:
1. Modo Padrão (últimos 2 dígitos) - quando range começa em múltiplo de 100
2. Modo Offset (sequencial) - quando range começa em outro número
"""

import json
import os


# Arquivo de configuração do IP Range
IP_CONFIG_FILE = "ip_range_config.json"


class IPMapping:
    """Gerencia mapeamento inteligente entre número de coletor e IP"""
    
    def __init__(self, base_ip="203.0.113", start_ip=100, end_ip=199):
        """
        Args:
            base_ip: Base do IP (ex: "203.0.113")
            start_ip: IP inicial (ex: 100)
            end_ip: IP final (ex: 199)
        """
        self.base_ip = base_ip
        self.start_ip = start_ip
        self.end_ip = end_ip
        
        # Detectar modo automaticamente
        self.mode = self._detect_mode()
    
    def _detect_mode(self):
        """
        Detecta qual modo usar baseado no IP inicial:
        - Modo 'digits': IP inicial é múltiplo de 100 (ex: 100, 200) 
        - Modo 'offset': IP inicial NÃO é múltiplo de 100 (ex: 2, 50)
        
        Returns:
            'digits' ou 'offset'
        """
        # Se o start_ip é múltiplo de 100, usa modo de últimos dígitos
        if self.start_ip % 100 == 0:
            return 'digits'
        else:
            return 'offset'
    
    def get_expected_ip(self, collector_number):
        """
        Calcula IP esperado para um número de coletor
        
        Args:
            collector_number: Número do coletor (int, ex: 0, 15, 58)
        
        Returns:
            IP esperado (str) ou None se fora do range
        
        Exemplos:
            Range 100-199, Coletor 15 → 203.0.113.115 (modo digits)
            Range 2-253, Coletor 15 → 203.0.113.17 (modo offset: 2+15=17)
        """
        if self.mode == 'digits':
            # Modo Padrão: Últimos 2 dígitos = número do coletor
            last_octet = self.start_ip + collector_number
            
            # Verificar se está no range
            if last_octet < self.start_ip or last_octet > self.end_ip:
                return None
            
            return f"{self.base_ip}.{last_octet}"
        
        else:
            # Modo Offset: IP = start_ip + collector_number
            last_octet = self.start_ip + collector_number
            
            # Verificar se está no range
            if last_octet < self.start_ip or last_octet > self.end_ip:
                return None
            
            return f"{self.base_ip}.{last_octet}"
    
    def get_collector_number(self, ip):
        """
        Calcula número do coletor a partir de um IP
        
        Args:
            ip: IP completo (str, ex: "203.0.113.115")
        
        Returns:
            Número do coletor (int) ou None se não puder determinar
        
        Exemplos:
            Range 100-199, IP 203.0.113.115 → 15 (modo digits: 115-100=15)
            Range 2-253, IP 203.0.113.17 → 15 (modo offset: 17-2=15)
        """
        try:
            # Extrair último octeto
            parts = ip.split('.')
            if len(parts) != 4:
                return None
            
            last_octet = int(parts[3])
            
            # Verificar se está no range
            if last_octet < self.start_ip or last_octet > self.end_ip:
                return None
            
            if self.mode == 'digits':
                # Modo Padrão: número = últimos 2 dígitos do último octeto
                # Mas precisa considerar o offset do start_ip
                collector_num = last_octet - self.start_ip
                return collector_num
            
            else:
                # Modo Offset: número = último_octeto - start_ip
                collector_num = last_octet - self.start_ip
                return collector_num
        
        except:
            return None
    
    def is_ip_correct(self, collector_number, actual_ip):
        """
        Verifica se o IP atual do coletor está correto
        
        Args:
            collector_number: Número do coletor (int)
            actual_ip: IP atual do coletor (str)
        
        Returns:
            True se correto, False se incorreto
        
        Exemplos:
            Range 100-199:
            - Coletor 15, IP 203.0.113.115 → True ✅
            - Coletor 15, IP 203.0.113.120 → False ❌
            
            Range 2-253:
            - Coletor 15, IP 203.0.113.17 → True ✅ (2+15=17)
            - Coletor 15, IP 203.0.113.115 → False ❌
        """
        expected_ip = self.get_expected_ip(collector_number)
        
        if expected_ip is None:
            return False
        
        return actual_ip == expected_ip
    
    def get_all_mappings(self):
        """
        Retorna todos os mapeamentos possíveis no range atual
        
        Returns:
            dict: {collector_number: expected_ip}
        
        Exemplo:
            Range 100-103 → {0: "203.0.113.100", 1: "203.0.113.101", ...}
        """
        mappings = {}
        
        # Calcular quantos coletores cabem no range
        total_ips = self.end_ip - self.start_ip + 1
        
        for i in range(total_ips):
            ip = self.get_expected_ip(i)
            if ip:
                mappings[i] = ip
        
        return mappings
    
    def get_mode_description(self):
        """
        Retorna descrição do modo atual
        
        Returns:
            str com explicação
        """
        if self.mode == 'digits':
            return (
                f"📊 Modo PADRÃO (Últimos 2 Dígitos)\n"
                f"   Range: {self.base_ip}.{self.start_ip} - {self.base_ip}.{self.end_ip}\n"
                f"   Regra: Coletor XX → {self.base_ip}.{self.start_ip + 0}XX\n"
                f"   Exemplo: Coletor 15 → {self.get_expected_ip(15)}"
            )
        else:
            return (
                f"📈 Modo OFFSET (Sequencial)\n"
                f"   Range: {self.base_ip}.{self.start_ip} - {self.base_ip}.{self.end_ip}\n"
                f"   Regra: Coletor N → {self.base_ip}.(Start + N)\n"
                f"   Exemplo: Coletor 15 → {self.get_expected_ip(15)} (offset: {self.start_ip}+15)"
            )
    
    def get_config_info(self):
        """
        Retorna informações da configuração atual
        
        Returns:
            dict com detalhes
        """
        mappings = self.get_all_mappings()
        
        return {
            'base_ip': self.base_ip,
            'start_ip': self.start_ip,
            'end_ip': self.end_ip,
            'mode': self.mode,
            'total_ips': self.end_ip - self.start_ip + 1,
            'total_collectors': len(mappings),
            'first_collector': f"Coletor 00 → {self.get_expected_ip(0)}",
            'last_collector': f"Coletor {len(mappings)-1:02d} → {self.get_expected_ip(len(mappings)-1)}",
            'description': self.get_mode_description()
        }
    
    @staticmethod
    def save_config(base_ip, start_ip, end_ip):
        """
        Salva configuração de IP Range
        
        Args:
            base_ip: Base do IP (str)
            start_ip: IP inicial (int)
            end_ip: IP final (int)
        """
        config = {
            'base_ip': base_ip,
            'start_ip': start_ip,
            'end_ip': end_ip,
            'updated_at': __import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        try:
            with open(IP_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def load_config():
        """
        Carrega configuração de IP Range
        
        Returns:
            tuple: (base_ip, start_ip, end_ip) ou valores padrão
        """
        if os.path.exists(IP_CONFIG_FILE):
            try:
                with open(IP_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return (
                        config.get('base_ip', '203.0.113'),
                        config.get('start_ip', 100),
                        config.get('end_ip', 199)
                    )
            except:
                pass
        
        # Valores padrão
        return ('203.0.113', 100, 199)
    
    @classmethod
    def from_config_file(cls):
        """
        Cria instância a partir do arquivo de configuração
        
        Returns:
            IPMapping instance
        """
        base_ip, start_ip, end_ip = cls.load_config()
        return cls(base_ip, start_ip, end_ip)


# ========== FUNÇÕES AUXILIARES ==========

def extract_collector_number_from_name(name):
    """
    Extrai número do coletor a partir do nome
    
    Args:
        name: Nome do coletor (ex: "Coletor 15", "Coletor REC 15")
    
    Returns:
        int com número ou None
    
    Exemplos:
        "Coletor 15" → 15
        "Coletor REC 15" → 15
        "Coletor 05" → 5
    """
    import re
    
    # Buscar padrão: "coletor" seguido de número
    match = re.search(r'coletor\s*0*?(\d+)\b', name, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except:
            pass
    
    return None


def check_collector_ip_mismatch(collector_name, collector_ip):
    """
    Verifica se coletor está com IP incorreto
    
    Args:
        collector_name: Nome do coletor (str)
        collector_ip: IP atual do coletor (str)
    
    Returns:
        bool: True se IP incorreto, False se correto
    
    Exemplos:
        Config 100-199:
        - ("Coletor 15", "203.0.113.115") → False (correto)
        - ("Coletor 15", "203.0.113.120") → True (incorreto)
        
        Config 2-253:
        - ("Coletor 15", "203.0.113.17") → False (correto: 2+15)
        - ("Coletor 15", "203.0.113.115") → True (incorreto)
    """
    # Extrair número do coletor
    collector_num = extract_collector_number_from_name(collector_name)
    if collector_num is None:
        return False  # Não conseguiu determinar
    
    # Carregar configuração atual
    mapper = IPMapping.from_config_file()
    
    # Verificar se IP está correto
    return not mapper.is_ip_correct(collector_num, collector_ip)


def get_expected_ip_for_collector(collector_name):
    """
    Retorna IP esperado para um coletor
    
    Args:
        collector_name: Nome do coletor (str)
    
    Returns:
        IP esperado (str) ou None
    
    Exemplos:
        Config 100-199:
        - "Coletor 15" → "203.0.113.115"
        
        Config 2-253:
        - "Coletor 15" → "203.0.113.17"
    """
    # Extrair número do coletor
    collector_num = extract_collector_number_from_name(collector_name)
    if collector_num is None:
        return None
    
    # Carregar configuração atual
    mapper = IPMapping.from_config_file()
    
    return mapper.get_expected_ip(collector_num)


# ========== EXEMPLOS DE USO ==========

if __name__ == "__main__":
    print("=" * 80)
    print("TESTES DO SISTEMA DE MAPEAMENTO IP/COLETOR")
    print("=" * 80)
    
    # Teste 1: Range padrão (100-199)
    print("\n[TESTE 1] Range 203.0.113.100-199 (Padrão)")
    mapper1 = IPMapping("203.0.113", 100, 199)
    print(mapper1.get_mode_description())
    print(f"\nVerificações:")
    print(f"  Coletor 15, IP 203.0.113.115 → {'✅ Correto' if mapper1.is_ip_correct(15, '203.0.113.115') else '❌ Incorreto'}")
    print(f"  Coletor 15, IP 203.0.113.120 → {'✅ Correto' if mapper1.is_ip_correct(15, '203.0.113.120') else '❌ Incorreto'}")
    
    # Teste 2: Range toda faixa (2-253)
    print("\n" + "=" * 80)
    print("[TESTE 2] Range 203.0.113.2-253 (Toda Faixa)")
    mapper2 = IPMapping("203.0.113", 2, 253)
    print(mapper2.get_mode_description())
    print(f"\nVerificações:")
    print(f"  Coletor 00 → {mapper2.get_expected_ip(0)}")
    print(f"  Coletor 15 → {mapper2.get_expected_ip(15)}")
    print(f"  Coletor 15, IP 203.0.113.17 → {'✅ Correto' if mapper2.is_ip_correct(15, '203.0.113.17') else '❌ Incorreto'}")
    print(f"  Coletor 15, IP 203.0.113.115 → {'✅ Correto' if mapper2.is_ip_correct(15, '203.0.113.115') else '❌ Incorreto'}")
    
    # Teste 3: Range híbrido (100-253)
    print("\n" + "=" * 80)
    print("[TESTE 3] Range 203.0.113.100-253 (Híbrido 1)")
    mapper3 = IPMapping("203.0.113", 100, 253)
    print(mapper3.get_mode_description())
    print(f"\nVerificações:")
    print(f"  Coletor 00 → {mapper3.get_expected_ip(0)}")
    print(f"  Coletor 15 → {mapper3.get_expected_ip(15)}")
    
    # Teste 4: Range híbrido (2-199)
    print("\n" + "=" * 80)
    print("[TESTE 4] Range 203.0.113.2-199 (Híbrido 2)")
    mapper4 = IPMapping("203.0.113", 2, 199)
    print(mapper4.get_mode_description())
    print(f"\nVerificações:")
    print(f"  Coletor 00 → {mapper4.get_expected_ip(0)}")
    print(f"  Coletor 15 → {mapper4.get_expected_ip(15)}")
    
    print("\n" + "=" * 80)