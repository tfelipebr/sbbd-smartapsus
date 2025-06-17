FROM smartapsus/otimizacao:0.1
EXPOSE 8080

ADD src/main/resources/facility_v1.py /facility_v1.py
ADD src/main/resources/facility_v3.py /facility_v3.py
ADD src/main/resources/facility_v4.py /facility_v4.py
ADD src/main/resources/entrada.json /entrada.json
ADD src/main/resources/entrada2.json /entrada2.json
ADD src/main/resources/entrada3.json /entrada3.json

ADD ./target/*.jar app.jar

ENTRYPOINT ["java", "-jar",  "/app.jar"]