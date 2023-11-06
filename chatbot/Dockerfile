# Start from a base image. 
FROM registry.boon.com.au/proxy-cache-docker-hub/library/python:3.11.6-slim-bookworm
#FROM python:3.12.0-slim-bookworm

EXPOSE 80

RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc build-essential libssl-dev libffi-dev python3-dev cmake && apt-get clean

RUN useradd -m boon

# Create the directory
RUN mkdir -p /opt/boon/.streamlit
RUN mkdir -p /opt/boon/questions
RUN mkdir -p /opt/boon/lib
RUN mkdir -p /opt/boon/agent-description
RUN chown -R boon:boon /opt/boon


# Set the Streamlit config directory
#ENV STREAMLIT_CONFIG_DIR /opt/boon
ENV PYTHONUNBUFFERED x
ENV TZ Australia/Perth

# Set the working directory inside the container
WORKDIR /opt/boon

# Copy the specified files into the container at /opt/boon
COPY requirements.txt .
COPY chatbot.py .
COPY .streamlit/config.toml .streamlit/
COPY questions/questions.txt questions/
COPY agent-description/*.txt agent-description/
COPY lib/boon.py lib/

RUN chown -R boon:boon /opt/boon 
# Install any dependencies from the requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

USER boon
# Command to run when the container starts
#CMD ["streamlit", "run", "chatbot.py", "--server.address=0.0.0.0", "--server.port=80", "--browser.gatherUsageStats=false" ]
CMD ["streamlit", "run", "chatbot.py"]