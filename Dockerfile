FROM openjdk:11-jdk
COPY --from=python:3.6 / /

#  Version
ENV   SOAPUI_VERSION  5.6.0

COPY entry_point.sh /opt/bin/entry_point.sh
COPY server.py /opt/bin/server.py
COPY server_index.html /opt/bin/server_index.html

RUN chmod +x /opt/bin/entry_point.sh
RUN chmod +x /opt/bin/server.py

# Download and unarchive SoapUI
RUN mkdir -p /opt &&\
    curl  https://s3.amazonaws.com/downloads.eviware/soapuios/${SOAPUI_VERSION}/SoapUI-${SOAPUI_VERSION}-linux-bin.tar.gz \
    | gunzip -c - | tar -xf - -C /opt && \
    ln -s /opt/SoapUI-${SOAPUI_VERSION} /opt/SoapUI

RUN chmod -R g+w /opt/SoapUI-${SOAPUI_VERSION}
RUN chmod -R g+w /opt/SoapUI

# hack for running soap ui
RUN rm /opt/SoapUI/lib/xmlbeans-xmlpublic-2.6.0.jar

# Set working directory
WORKDIR /opt/bin

# Set environment
ENV PATH ${PATH}:/opt/SoapUI/bin

EXPOSE 3000
CMD ["/opt/bin/entry_point.sh"]
