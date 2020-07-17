FROM gcr.io/airspot//rulesset-image-base:0.1.52

ADD ./app /app

# nice to have an interactive shell
RUN pip install ipython
ADD ipython_config.py /root/.ipython/profile_default/

# uncomment for subjects redis support
RUN pip install  krules-subjects-storage-redis==0.2.4
# uncomment for subjects mongodb support
# RUN pip install -e git+https://krules_guest:kr-guest-sDDsvCXA@gitlab.com/krules/krules-subjects-mongodb-storage.git#egg=krules-subjects-mongodb-storage-0.1.0

RUN pip install cloudstorage
RUN pip install cloudstorage[google]
RUN pip install pymongo
