FROM debian as gym-2048
WORKDIR /app/gym-2048/
#
# Setting environment for fully non-interactive system
# package installation.
#
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true
#
RUN apt-get update -y
RUN apt-get install python3-pip -y
#
# Copy the package files, etc.
#
COPY add_rewards_to_training_data.py /app/gym-2048/
COPY augment_training_data.py /app/gym-2048/
COPY distribute_training_data.py /app/gym-2048/ 
COPY gather_training_data.py /app/gym-2048/
COPY ["gym_2048/", "/app/gym-2048/gym_2048/"]
COPY hflip_training_data.py /app/gym-2048/
COPY LICENSE.txt /app/gym-2048/
COPY merge_training_data.py /app/gym-2048/
COPY params.json /app/gym-2048/
COPY README.md /app/gym-2048/
COPY requirements.txt /app/gym-2048/
COPY setup.py /app/gym-2048/
COPY test_data.csv /app/gym-2048/
COPY test-requirements.txt /app/gym-2048/
COPY test_training_data.py /app/gym-2048/
COPY training_data.py /app/gym-2048/
COPY train_keras_model.py /app/gym-2048/
#
# Install Python dependencies
#
RUN pip install -r requirements.txt
#
# Start model run.
#
CMD python3 train_keras_model.py test_data.csv
