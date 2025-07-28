# Sistema de Monitoramento Veicular

Sistema completo de monitoramento veicular desenvolvido em Django com integração à API Flespi e rastreadores Coban GPS303-F. O sistema oferece rastreamento em tempo real, gestão de viagens, relatórios e controle de combustível e manutenção.

## 🚗 Funcionalidades Principais

### Para Administradores
- ✅ Gestão completa de usuários, veículos e dispositivos
- ✅ Configuração do sistema e parâmetros da API Flespi
- ✅ Acesso a todos os relatórios e dados
- ✅ Gerenciamento de permissões

### Para Gestores
- ✅ Gerenciamento de veículos e motoristas
- ✅ Controle de viagens e rotas
- ✅ Monitoramento em tempo real
- ✅ Gestão de combustível e serviços
- ✅ Geração de relatórios detalhados

### Para Motoristas
- ✅ Visualização de veículos designados
- ✅ Registro e acompanhamento de viagens próprias
- ✅ Acesso limitado aos dados do sistema

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.13+**
- **Django 5.2** - Framework web principal
- **Django REST Framework** - APIs REST
- **Django Channels** - WebSocket para tempo real
- **SQLite3** - Banco de dados (configurável para PostgreSQL)
- **ReportLab** - Geração de relatórios PDF

### Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **Leaflet.js** - Mapas interativos
- **Chart.js** - Gráficos e estatísticas
- **Bootstrap Icons** - Ícones

### Integração
- **API Flespi** - Telemetria dos dispositivos Coban GPS303-F
- **WebSocket** - Atualizações em tempo real

## 📋 Pré-requisitos

- Python 3.13 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Conta na plataforma Flespi (para integração com dispositivos)

## 🚀 Instalação

### 1. Clonar o Repositório
```bash
git clone <url-do-repositorio>
cd vehicle-monitoring-system
```

### 2. Criar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Edite o arquivo `.env` com suas configurações:
```env
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
FLESPI_TOKEN=seu_token_flespi_aqui
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Executar Migrações
```bash
python manage.py migrate
```

### 6. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 7. Iniciar o Servidor
```bash
python manage.py runserver
```

O sistema estará disponível em: `http://localhost:8000`

## 👤 Credenciais de Demonstração

**Administrador:**
- Usuário: `admin`
- Senha: `admin123`

## 📱 Estrutura do Sistema

### Aplicações Django

1. **accounts** - Gerenciamento de usuários e autenticação
2. **vehicles** - Gestão de veículos, viagens e serviços
3. **tracking** - Rastreamento e telemetria
4. **reports** - Sistema de relatórios

### Modelos Principais

#### Usuários (accounts/models.py)
- `User` - Usuário personalizado com tipos (Admin, Gestor, Motorista)

#### Veículos (vehicles/models.py)
- `Vehicle` - Informações dos veículos
- `TrackingDevice` - Dispositivos de rastreamento
- `Trip` - Viagens e rotas
- `FuelRecord` - Registros de combustível
- `ServiceRecord` - Registros de manutenção

#### Rastreamento (tracking/models.py)
- `LocationData` - Dados de localização em tempo real
- `GeofenceArea` - Áreas de geofence
- `GeofenceAlert` - Alertas de geofence
- `SpeedAlert` - Alertas de velocidade
- `MaintenanceAlert` - Alertas de manutenção

## 🗺️ APIs REST

### Endpoints Principais

#### Veículos
- `GET /dashboard/api/vehicles/` - Lista veículos
- `POST /dashboard/api/vehicles/` - Criar veículo
- `GET /dashboard/api/vehicles/{id}/` - Detalhes do veículo
- `GET /dashboard/api/vehicles/{id}/current_location/` - Localização atual
- `GET /dashboard/api/vehicles/{id}/location_history/` - Histórico de localização

#### Viagens
- `GET /dashboard/api/trips/` - Lista viagens
- `POST /dashboard/api/trips/` - Criar viagem
- `POST /dashboard/api/trips/{id}/start_trip/` - Iniciar viagem
- `POST /dashboard/api/trips/{id}/end_trip/` - Finalizar viagem

#### Combustível
- `GET /dashboard/api/fuel-records/` - Registros de combustível
- `POST /dashboard/api/fuel-records/` - Adicionar registro

#### Serviços
- `GET /dashboard/api/service-records/` - Registros de serviços
- `POST /dashboard/api/service-records/` - Adicionar registro

## 🔧 Configuração da API Flespi

### 1. Criar Conta na Flespi
1. Acesse [flespi.io](https://flespi.io)
2. Crie uma conta gratuita
3. Obtenha seu token de API

### 2. Configurar Dispositivos
1. No painel Flespi, crie um canal para dispositivos Coban GPS303-F
2. Configure os dispositivos com os parâmetros de conexão
3. Anote os IDs dos dispositivos

### 3. Configurar no Sistema
1. Adicione o token Flespi no arquivo `.env`
2. No admin Django, crie registros de `TrackingDevice` com os IDs dos dispositivos
3. Associe os dispositivos aos veículos

## 📊 Sistema de Relatórios

### Tipos de Relatórios Disponíveis

1. **Relatório de Viagens**
   - Filtros: período, veículo, status
   - Exportação: PDF, CSV
   - Dados: origem, destino, duração, combustível

2. **Relatório de Combustível**
   - Filtros: período, veículo
   - Estatísticas: consumo total, custo médio
   - Gráficos de tendência

3. **Relatório de Serviços**
   - Filtros: período, tipo de serviço, veículo
   - Custos de manutenção
   - Histórico de serviços

### Geração de Relatórios
```python
# Exemplo de uso da API de relatórios
from reports.views import export_trips_report

# Exportar relatório de viagens em PDF
response = export_trips_report(request, format='pdf')
```

## 🗺️ Sistema de Mapas

### Funcionalidades do Mapa
- **Visualização em tempo real** dos veículos
- **Histórico de trajetos** com filtros de data
- **Geofencing** com alertas de entrada/saída
- **Marcadores personalizados** por status do veículo

### Integração Leaflet.js
```javascript
// Exemplo de inicialização do mapa
var map = L.map('map').setView([-25.9664, 32.5832], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Adicionar marcadores de veículos
vehicles.forEach(function(vehicle) {
    L.marker([vehicle.latitude, vehicle.longitude])
        .addTo(map)
        .bindPopup(vehicle.plate);
});
```

## 🔐 Sistema de Permissões

### Níveis de Acesso

1. **Administrador**
   - Acesso total ao sistema
   - Gerenciamento de usuários
   - Configurações do sistema

2. **Gestor**
   - Gerenciamento de veículos e motoristas
   - Visualização de todos os dados
   - Geração de relatórios

3. **Motorista**
   - Acesso limitado aos próprios dados
   - Visualização de veículos designados
   - Registro de viagens próprias

### Implementação
```python
# Exemplo de verificação de permissões
@login_required
def vehicle_list(request):
    if request.user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=request.user)
    else:
        vehicles = Vehicle.objects.all()
    return render(request, 'vehicles/list.html', {'vehicles': vehicles})
```

## 🚨 Sistema de Alertas

### Tipos de Alertas

1. **Alertas de Geofence**
   - Entrada/saída de áreas definidas
   - Violação de áreas restritas

2. **Alertas de Velocidade**
   - Excesso de velocidade
   - Configurável por veículo

3. **Alertas de Manutenção**
   - Combustível baixo
   - Bateria baixa
   - Manutenção programada

## 📱 Interface Responsiva

### Características
- **Design responsivo** com Bootstrap 5
- **Sidebar colapsível** para navegação
- **Dashboard intuitivo** com widgets informativos
- **Tabelas responsivas** com filtros e paginação

### Componentes Principais
- Cards de estatísticas
- Tabelas de dados com DataTables
- Formulários com validação
- Mapas interativos
- Gráficos e charts

## 🧪 Testes

### Executar Testes
```bash
# Executar todos os testes
python manage.py test

# Executar testes com coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Estrutura de Testes
```python
# Exemplo de teste
from django.test import TestCase
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle

User = get_user_model()

class VehicleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            user_type='manager'
        )
        
    def test_create_vehicle(self):
        vehicle = Vehicle.objects.create(
            plate='ABC-1234',
            brand='Toyota',
            model='Corolla',
            year=2020,
            fuel_capacity=50.0
        )
        self.assertEqual(vehicle.plate, 'ABC-1234')
```

## 🔄 Sincronização de Dados

### Processo de Sincronização
1. **Coleta automática** de dados da API Flespi
2. **Processamento** de telemetria em tempo real
3. **Armazenamento** no banco de dados local
4. **Geração de alertas** baseados em regras

### Comando de Sincronização
```bash
# Sincronizar dados de todos os dispositivos
python manage.py shell -c "from tracking.services import sync_all_devices; sync_all_devices()"
```

## 📈 Monitoramento e Logs

### Sistema de Logs
- Logs de aplicação em `logs/django.log`
- Logs de erro e debug
- Rastreamento de atividades dos usuários

### Configuração de Logs
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'vehicle_monitoring': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 Deploy em Produção

### Preparação para Produção
1. **Configurar PostgreSQL** (recomendado)
2. **Configurar variáveis de ambiente** de produção
3. **Configurar servidor web** (Nginx + Gunicorn)
4. **Configurar SSL/HTTPS**
5. **Configurar backup automático**

### Exemplo de Configuração Nginx
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Padrões de Código
- Seguir PEP 8 para Python
- Usar Black para formatação
- Documentar funções e classes
- Escrever testes para novas funcionalidades

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Abra uma issue no GitHub
- Entre em contato através do email: suporte@vehicletrack.com

## 🔄 Changelog

### v1.0.0 (2024)
- ✅ Sistema base de monitoramento veicular
- ✅ Integração com API Flespi
- ✅ Dashboard responsivo com Bootstrap 5
- ✅ Sistema de usuários com permissões
- ✅ Relatórios em PDF e CSV
- ✅ Mapas interativos com Leaflet.js
- ✅ Sistema de alertas
- ✅ APIs REST completas

---

**Desenvolvido para o mercado moçambicano com foco em eficiência e usabilidade.**