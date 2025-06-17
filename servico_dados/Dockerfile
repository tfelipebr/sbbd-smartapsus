FROM openjdk:17.0.1-jdk-slim
EXPOSE 8080

ADD src/main/resources/previsao/ /previsao/
ADD ./target/*.jar app.jar

# Atualiza os pacotes e instala Python e bibliotecas básicas
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-matplotlib

# Instala as dependências do Python listadas no requirements.txt
RUN pip install -r /previsao/requirements.txt

# Define o ponto de entrada para a aplicação
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=80", "-jar", "/app.jar"]
