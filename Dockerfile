# Sử dụng image Python chính thức, phiên bản nhẹ.
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container.
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho pyodbc (MSSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Thêm kho chứa chính thức của Microsoft cho ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Cài đặt ODBC driver cho SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Sao chép tệp requirements và cài đặt các thư viện Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng vào container.
COPY ./app /app
