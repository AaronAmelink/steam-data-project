FROM ubuntu:latest

# update data from apt-get repositories
RUN apt-get update && \
    apt-get -y install unzip && \
    apt-get -y install curl && \
    apt-get -y install gnupg && \
    apt-get -y install wget && \
    apt-get -y install cron && \
    apt-get -y install libodbc2
RUN apt-get install python3-pip -y
# Add Microsoft repository key and source list
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl -sSL https://packages.microsoft.com/config/debian/11/prod.list \
    -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 && \
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc && \
    apt-get install -y unixodbc-dev libgssapi-krb5-2 && \
    rm -rf /var/lib/apt/lists/*


ENV PATH="$PATH:/opt/mssql-tools18/bin"
# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY python-cron/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt

# Copy crontab
COPY crontab.txt /etc/cron.d/app-cron

# Set up cron
RUN chmod 0644 /etc/cron.d/app-cron && \
    touch /var/log/cron.log

# Copy application code
COPY . /app

# Copy entrypoint script
COPY python-cron/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN find . -type f -name "*.sh" -exec chmod +x {} \;

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["tail", "-f", "/var/log/cron.log"]

