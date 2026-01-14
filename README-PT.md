<div align="center">
  
![AWS Route 53](https://img.icons8.com/color/96/amazon-web-services.png)

# Camada de Abstração de DNS Interno para Amazon RDS e Aurora

**Atualizado: 14 de Janeiro de 2026**

[![Follow @nicoleepaixao](https://img.shields.io/github/followers/nicoleepaixao?label=Follow&style=social)](https://github.com/nicoleepaixao)
[![Star this repo](https://img.shields.io/github/stars/nicoleepaixao/aws-internal-rds-dns-layer?style=social)](https://github.com/nicoleepaixao/aws-internal-rds-dns-layer)
[![Medium Article](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://nicoleepaixao.medium.com/)

<p align="center">
  <a href="README-PT.md">🇧🇷</a>
  <a href="README.md">🇺🇸</a>
</p>

</div>

---
<p align="center">
  <img src="img/aws-internal-rds-dns-layer.png" alt="Internal RDS DNS Layer Architecture" width="1800">
</p>

## **Visão Geral**

Este repositório fornece uma implementação de referência completa para projetar e implantar uma camada de DNS interno que mascara endpoints do Amazon RDS e Aurora. O objetivo é desacoplar aplicações de hostnames de banco de dados gerados pela AWS, introduzindo um padrão de nomenclatura DNS privado consistente usando **Route 53 Private Hosted Zones**.

---

## **Informações Importantes**

### **O Desafio**

| **Aspecto** | **Detalhes** |
|------------|-------------|
| **Problema** | Aplicações consomem diretamente endpoints RDS/Aurora gerados pela AWS |
| **Risco** | Acoplamento forte torna migrações, upgrades e failovers arriscados |
| **Complexidade** | Difícil de governar através de múltiplos ambientes |
| **Impacto de Mudanças** | Deployments blue/green requerem mudanças no código da aplicação |
| **Segurança** | Exposição direta de hostnames gerados pela AWS |

### **A Solução**

A AWS gera endpoints únicos de RDS e Aurora que frequentemente mudam durante upgrades, deployments blue/green ou substituições de cluster. Aplicações que consomem diretamente esses endpoints ficam fortemente acopladas à infraestrutura, aumentando o risco operacional.

Este projeto introduz uma abstração de DNS interno usando **Route 53 Private Hosted Zones**, permitindo que aplicações e engenheiros se conectem a bancos de dados usando nomes estáveis, legíveis e agnósticos ao ambiente.

**Exemplos de Nomes DNS Internos:**

```
orders-db-dev.internal.example
orders-aurora-prd.internal.example
orders-aurora-prd-ro.internal.example
```

Esses hostnames internos resolvem apenas dentro de VPCs e conexões VPN, aumentando tanto a segurança quanto a flexibilidade.

### **Benefícios do Projeto**

✅ **Aplicações Desacopladas**: Sem necessidade de mudanças de código para migrações de banco de dados  
✅ **Nomenclatura Consistente**: Convenção DNS padronizada através de todos os ambientes  
✅ **Segurança Aprimorada**: Resolução interna apenas (VPC + VPN)  
✅ **Flexibilidade Operacional**: Upgrades, failovers e deployments blue/green seguros  
✅ **Suporte Multi-Conta**: Modelo escalável para AWS Organizations

---

## **Arquitetura**

<p align="center">
  <img src="img/aws-internal-rds-dns-layer.png" alt="Internal RDS DNS Layer Architecture" width="1800">
</p>

**Fluxo de Resolução:**

1. Aplicação ou usuário VPN consulta `orders-db-prd.internal.example`
2. VPC DNS Resolver encaminha para Route 53 Private Hosted Zone
3. Private Hosted Zone retorna CNAME para endpoint RDS real
4. Conexão estabelecida com o banco de dados real

---

## **Funcionalidades**

| **Funcionalidade** | **Descrição** |
|-------------|-----------------|
| **Descoberta Automatizada** | Script Python + Boto3 para inventário RDS/Aurora |
| **Inventário Completo** | Escaneia através de múltiplas contas e regiões |
| **Convenção de Nomenclatura** | Template DNS interno padronizado |
| **Diagrama de Arquitetura** | Referência visual para camada de abstração DNS |
| **Suporte Writer & Reader** | Gerencia ambos endpoints de cluster |
| **Pronto Multi-Conta** | Ideal para AWS Organizations |
| **Exportações CSV** | Inventário e exemplos de mapeamento DNS incluídos |

---

## **Padrão de Nomenclatura DNS Interno**

### **Convenção**

```
<serviço>-<tipo>-<ambiente>.internal.<domínio>
```

### **Exemplos**

| **Serviço** | **Tipo** | **Ambiente** | **DNS Interno** |
|-------------|----------|-----------------|------------------|
| billing | db | dev | `billing-db-dev.internal.example` |
| billing | aurora | prd | `billing-aurora-prd.internal.example` |
| billing | aurora | prd (reader) | `billing-aurora-prd-ro.internal.example` |
| orders | db | hom | `orders-db-hom.internal.example` |

---

## **Como Começar**

### **1. Clonar Repositório**

```bash
git clone https://github.com/nicoleepaixao/aws-internal-rds-dns-layer.git
cd aws-internal-rds-dns-layer
```

### **2. Configurar Perfis AWS**

Certifique-se de que seus perfis AWS estão configurados em `~/.aws/config`:

```ini
[profile dev-account]
region = us-east-1
output = json

[profile staging-account]
region = us-east-1
output = json

[profile prod-account]
region = us-east-1
output = json
```

### **3. Instalar Dependências**

```bash
pip install boto3
```

### **4. Executar Script de Inventário**

```bash
python scripts/rds_inventory.py
```

**Saída:** Arquivo CSV com timestamp: `rds_inventory_20251202T123045Z.csv`

**Nota:** O script escaneia todas as contas e regiões configuradas para instâncias RDS e clusters Aurora.

---

## **Executando o Script de Inventário**

### **Configuração do Script**

Edite `scripts/rds_inventory.py` para customizar:

```python
ACCOUNTS = [
    {"profile": "dev-account", "alias": "dev"},
    {"profile": "staging-account", "alias": "staging"},
    {"profile": "prod-account", "alias": "prod"},
]

REGIONS = ["us-east-1", "sa-east-1"]
```

### **Execução**

```bash
python scripts/rds_inventory.py
```

### **Saída Contém**

- Perfil e ID da conta
- Região
- Tipo de recurso (instance, cluster-writer, cluster-reader)
- Identificador do banco de dados
- Engine e versão
- Endpoint AWS real
- Porta

---

## **Entendendo a Saída**

### **Amostra de Inventário (inventory_sample.csv)**

Dados brutos coletados pelo script Python:

| account_profile | account_alias | region | resource_type | identifier | engine | endpoint | port |
|-----------------|---------------|--------|---------------|------------|--------|----------|------|
| dev-account | dev | us-east-1 | instance | orders-db-dev | postgres | orders-db-dev.c1abcxyz123.us-east-1.rds.amazonaws.com | 5432 |
| prod-account | prod | us-east-1 | cluster-writer | orders-aurora-prd | aurora-postgresql | orders-aurora-prd.cluster-prd123abcd.us-east-1.rds.amazonaws.com | 5432 |
| prod-account | prod | us-east-1 | cluster-reader | orders-aurora-prd | aurora-postgresql | orders-aurora-prd.cluster-ro-prd123abcd.us-east-1.rds.amazonaws.com | 5432 |

### **Exemplo de Mapeamento DNS (dns_mapping_example.csv)**

Mapeamento final com nomes DNS internos aplicados:

| service | environment | type | real_endpoint | internal_dns |
|---------|-------------|------|---------------|--------------|
| orders | dev | db | orders-db-dev.c1abcxyz123.us-east-1.rds.amazonaws.com | orders-db-dev.internal.example |
| orders | prd | aurora-writer | orders-aurora-prd.cluster-prd123abcd.us-east-1.rds.amazonaws.com | orders-aurora-prd.internal.example |
| orders | prd | aurora-reader | orders-aurora-prd.cluster-ro-prd123abcd.us-east-1.rds.amazonaws.com | orders-aurora-prd-ro.internal.example |

---

## **Passos de Implementação**

### **Fase 1: Descoberta**

1. Executar script de inventário através de todas as contas
2. Gerar CSV com todos os recursos RDS/Aurora
3. Revisar e validar dados coletados

### **Fase 2: Design**

1. Definir convenção de nomenclatura DNS interno
2. Criar planilha de mapeamento DNS
3. Planejar estrutura de Private Hosted Zone

### **Fase 3: Deployment**

1. Criar Route 53 Private Hosted Zone (`internal.example`)
2. Associar PHZ com VPCs
3. Criar registros CNAME mapeando nomes internos para endpoints reais
4. Testar resolução DNS da VPC e VPN

### **Fase 4: Migração**

1. Atualizar configurações de aplicação com nomes DNS internos
2. Testar conectividade em ambientes de não-produção
3. Implantar em aplicações de produção
4. Desativar referências diretas a endpoints

---

## **Por Que Isso Importa**

| **Benefício** | **Impacto** |
|-------------|------------|
| **Desacoplamento de Aplicação** | Zero mudanças de código para migrações de banco de dados |
| **Operações Simplificadas** | Upgrades e deployments blue/green seguros |
| **Segurança Aprimorada** | Sem exposição pública de endpoints gerados pela AWS |
| **Melhor Governança** | Nomenclatura consistente através de todos os ambientes |
| **Failovers Suaves** | Substituições de cluster transparentes |
| **Otimização de Custos** | Mais fácil testar e migrar para tipos de instância mais novos |

---

## **Casos de Uso**

Esta camada de abstração DNS é ideal para:

- **Migrações de Banco de Dados**: Substituir instâncias RDS sem tocar no código da aplicação
- **Deployments Blue/Green**: Alternar entre clusters de banco de dados perfeitamente
- **Gerenciamento Multi-Ambiente**: Nomenclatura consistente através de dev/staging/prod
- **Recuperação de Desastres**: Failover rápido para regiões de backup
- **Upgrades de Versão**: Testar novas versões de engine sem mudanças na aplicação
- **Organizações Multi-Conta**: Padronizar DNS através de contas AWS

---

## **Tecnologias Utilizadas**

| **Tecnologia** | **Versão** | **Propósito** |
|----------------|-------------|-------------|
| Python | 3.8+ | Automação e script de inventário |
| boto3 | Mais recente | SDK AWS para chamadas API RDS/Aurora |
| Route 53 | - | Private Hosted Zones e gerenciamento DNS |
| AWS RDS | - | Serviço de banco de dados relacional |
| Amazon Aurora | - | Banco de dados relacional nativo da nuvem |

---

## **Estrutura do Projeto**

```text
aws-internal-rds-dns-layer/
│
├── README.md                      # Documentação completa do projeto
│
├── scripts/
│   └── rds_inventory.py           # Script Python de automação de inventário
│
├── examples/
│   ├── inventory_sample.csv       # Exemplo de inventário bruto RDS/Aurora
│   └── dns_mapping_example.csv    # Exemplo de mapeamento DNS interno
│
├── architecture/
│   └── dns-architecture-diagram.txt  # Diagrama de arquitetura ASCII
│
└── .gitignore                     # Arquivos ignorados (*.csv, .env, etc.)
```

---

## **Informações Adicionais**

Para mais detalhes sobre AWS RDS, Aurora e Route 53 Private DNS, consulte:

- [Amazon RDS Documentation](https://docs.aws.amazon.com/rds/) - Referência completa RDS
- [Amazon Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/) - Guia do usuário Aurora
- [Route 53 Private Hosted Zones](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html) - Configuração DNS
- [boto3 RDS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html) - Python SDK

---

## **Conecte-se & Siga**

Mantenha-se atualizado com automação de infraestrutura AWS e melhores práticas:

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nicoleepaixao)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white&style=for-the-badge)](https://www.linkedin.com/in/nicolepaixao/)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@nicoleepaixao)

</div>

---

## **Aviso Legal**

Esta implementação é fornecida como arquitetura de referência. Configurações, preços e disponibilidade de serviços AWS podem variar por região. Sempre teste resolução DNS completamente em ambientes de não-produção antes de implantar em produção. Consulte a documentação oficial da AWS para informações mais atuais.

---

<div align="center">

**Construa arquiteturas AWS resilientes com confiança!**

*Documento Criado: 7 de Dezembro de 2025*

Made with ❤️ by [Nicole Paixão](https://github.com/nicoleepaixao)

</div>
