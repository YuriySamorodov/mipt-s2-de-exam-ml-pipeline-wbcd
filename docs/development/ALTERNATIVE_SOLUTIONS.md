# WSL2 / Linux VM решение для macOS

## Опция A: WSL2 на Windows (через Parallels/VMware)

### Установка:
1. Установите Parallels Desktop или VMware Fusion
2. Создайте Windows 11 VM
3. Установите WSL2 в Windows VM:
```powershell
wsl --install -d Ubuntu-22.04
```

### Настройка Airflow в WSL2:
```bash
# В Ubuntu WSL2
sudo apt update && sudo apt install -y python3-pip postgresql postgresql-contrib
sudo service postgresql start

# Создание пользователя и базы данных
sudo -u postgres createuser -s airflow_user
sudo -u postgres createdb airflow_metadata
sudo -u postgres psql -c "ALTER USER airflow_user PASSWORD 'airflow_password';"

# Установка Airflow
pip install apache-airflow[postgres]
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://airflow_user:airflow_password@localhost:5432/airflow_metadata
export AIRFLOW__CORE__EXECUTOR=LocalExecutor

airflow db init
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin

# Запуск без zombie процессов!
airflow scheduler &
airflow webserver -p 8080
```

## Опция B: Linux VM (Ubuntu/CentOS)

### Создание VM:
1. Скачайте Ubuntu 22.04 LTS ISO
2. Создайте VM в Parallels/VMware (4GB RAM, 20GB диск)
3. Установите Ubuntu

### Настройка сети:
- Bridged mode для прямого доступа с macOS
- Port forwarding: 8080 -> 8080 для Airflow webserver

### Преимущества:
Нет zombie процессов (Linux kernel)
Полная совместимость с Airflow
Production-like окружение
Можно использовать Docker внутри VM

### Недостатки:
Требует дополнительные ресурсы
Более сложная настройка
Медленнее нативного macOS

## Опция C: Colima (Docker для macOS)

### Установка Colima:
```bash
brew install colima docker docker-compose

# Запуск Colima (альтернатива Docker Desktop)
colima start --cpu 4 --memory 8

# Проверка
docker ps
```

### Использование с Airflow:
```bash
# Использовать docker-compose из проекта
docker-compose up -d
```

### Преимущества:
Бесплатная альтернатива Docker Desktop
Легче VM
Хорошая интеграция с macOS
