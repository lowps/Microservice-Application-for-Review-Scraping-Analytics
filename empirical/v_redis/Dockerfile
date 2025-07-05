FROM redis:latest
 
WORKDIR /

COPY ./entrypoint.sh /


RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]