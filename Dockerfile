FROM continuumio/anaconda3

RUN apt-get update
RUN apt-get -y install vim
RUN conda create -n py39 python=3.9 pip
RUN echo "source activate py39" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

# Set the working directory inside the container
WORKDIR /usr/src/app
COPY . .
# Create a directory to mount the home directory
RUN mkdir /home_mount

# Install any needed packages specified in requirements.txt
#RUN conda install --file requirements.txt

RUN mkdir -p /opt/notebooks
RUN /opt/conda/envs/py39/bin/pip install -r requirements.txt

#RUN conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
#RUN conda install -c conda-forge transformers 
#RUN conda install tqdm pandas numpy tweepy


# Run Jupyter Notebook when the container launches
CMD ["bash"]