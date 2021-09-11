source /kaggle/input/voc2007/init

rm -r /kaggle/faster-rcnn.pytorch
if [ ! -e '/kaggle/faster-rcnn.pytorch' ]; then
    cd /kaggle
    echo 'Download faster-rcnn.pytorch.tar.bz2'
    wget -q https://raw.githubusercontent.com/loaxsc/ghdrive/main/faster-rcnn.pytorch.tar.bz2
    tar -jxf faster-rcnn.pytorch.tar.bz2
    rm faster-rcnn.pytorch.tar.bz2

    cd /kaggle/faster-rcnn.pytorch/
    echo 'pip install ...'
    #pip install -r requirements.txt 'git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI'
    pip --disable-pip-version-check install easydict \
        'git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI' # Simpler version
fi

if [ "$(which nvidia-smi)" ]; then
    cd /kaggle/faster-rcnn.pytorch/lib
    python setup.py develop
else
    echo '\nNot in GPU mode, exit !'
    exit
fi

cd /kaggle/faster-rcnn.pytorch/
mkdir -p data data/VOCdevkit2007 data/pretrained_model
ln -snf /kaggle/VOC2007 data/VOCdevkit2007/VOC2007
ln -snf /kaggle/working models

cd data/pretrained_model/
ln -snf /kaggle/input/od-models/resnet101_caffe.pth resnet101_caffe.pth
ln -snf /kaggle/input/vgg16-caffe/vgg16_caffe.pth vgg16_caffe.pth

echo "\nfaster-rcnn file prepared ok."
