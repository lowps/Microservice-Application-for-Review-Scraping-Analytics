FROM nginx:latest

COPY ./default.conf /etc/nginx/conf.d/default.conf 

# link nginx logs to container stdout
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

# COPY ./entrypoint.sh /

# # Make the entrypoint script executable
# RUN chmod +x /entrypoint.sh

# ENTRYPOINT ["/entrypoint.sh"]
