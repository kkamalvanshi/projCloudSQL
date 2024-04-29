from app import app
from extensions import db
from models import Model, Dataset, Version, Server, ModelDeployment
import random
from datetime import datetime, timedelta

def generate_random_date_int(start_year, start_month, start_day, end_year, end_month, end_day):
    """
    Generates a random date between two specified dates and converts it to an integer format like "101" for January 1st.
    
    Args:
        start_year, start_month, start_day: Start date components.
        end_year, end_month, end_day: End date components.
        
    Returns:
        An integer representing the random date in the specified format.
    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    # Generate a random date between start_date and end_date
    delta = end_date - start_date
    random_days = random.randrange(delta.days + 1)
    random_date = start_date + timedelta(days=random_days)
    
    # Convert the random date to the specified integer format
    date_int = random_date.month * 100 + random_date.day
    return date_int

# Sample data for seeding
model_names = [
    "ChatGPT", "Claude", "Stable Diffusion", "BERT", "GPT-3", "RoBERTa", "Linear Regression", "Logistic Regression", 
    "SVM", "Random Forest", "XGBoost", "AdaBoost", "Naive Bayes", "KNN", "Decision Trees", "GPT-2", "GPT-Neo", "ELECTRA",
    "YOLOv4", "FastAI", "Prophet", "ARIMA", "LSTM", "GRU", "CNN", "ResNet", "VGG16", "InceptionV3", "MobileNet", "EfficientNet",
    "DALL-E", "CycleGAN", "U-Net", "R-CNN", "Fast R-CNN", "Mask R-CNN", "RetinaNet", "Transformer", "T5", "BART", "ERNIE", 
    "ALBERT", "XLNet", "WaveNet", "DeepLab", "Capsule Network", "Flair", "DistilBERT"
]

dataset_names = [
    "10B Parameter Tokens", "Zillow Dataset", "ImageNet", "COCO", "MNIST", "Fashion MNIST", "CIFAR-10", "CIFAR-100", 
    "20 Newsgroups", "Reuters-21578", "IMDb Reviews", "Amazon Product Reviews", "Google Speech Commands", "LibriSpeech", 
    "SQuAD", "GLUE Benchmark", "SuperGLUE Benchmark", "Stanford Sentiment Treebank", "Flickr30k", "Cityscapes", 
    "PASCAL VOC", "Affective Text", "TREC Question Classification", "UCI Machine Learning Repository", "Kaggle Datasets",
    "EuroSAT", "Spam Text Message Data", "YouTube-8M", "GoEmotions", "Open Images Dataset", "DeepFashion", "CelebA", "LFW",
    "CASIA WebFace", "VGGFace2", "MS-Celeb-1M", "YouTube Faces DB", "QuickDraw Dataset", "GTSRB", "TT100K", "BSDS500", 
    "NYU Depth V2", "KITTI Vision Benchmark", "DAVIS", "VOT Challenge", "AloT Dataset", "BigEarthNet", "Aerial Image Dataset",
    "Satellite Imagery Multi-vehicles Dataset", "NWPU-RESISC45", "UC Merced Land Use Dataset"
]

server_providers = [
    "Heroku", "GCP", "AWS", "Azure", "DigitalOcean", "Linode", "Vultr", "IBM Cloud", "Oracle Cloud", "Alibaba Cloud",
    "Cloudflare Workers", "Kamatera", "UpCloud", "StackPath", "OVHcloud", "Rackspace", "Navisite", "DreamHost",
    "Liquid Web", "A2 Hosting", "AccuWeb", "Bluehost", "GoDaddy", "HostGator", "Hostwinds", "InMotion", "iPage",
    "Media Temple", "SiteGround", "Aruba Cloud", "CloudSigma", "Hetnix", "Leaseweb", "Scaleway", "Tencent Cloud",
    "Baidu Cloud", "Jelastic", "Kinsta", "InterServer", "Hostinger", "FatCow", "GreenGeeks", "ServerPronto", "LunarPages",
    "Namecheap", "ResellerClub", "JustHost", "HostPapa", "HostMonster"
]

def seed_data():
    db.drop_all()
    db.create_all()

    # Seed Models
    for _ in range(1000):
        name = random.choice(model_names)
        if 'GPT' in name or 'BERT' in name or 'Transformer' in name:
            model_type = 'LLM'
        elif 'Regression' in name:
            model_type = 'Regression'
        else:
            model_type = 'Neural Network'
        db.session.add(Model(name=name, description=f'{name} model description.', type=model_type))

    # Seed Datasets
    for _ in range(1000):
        name = random.choice(dataset_names)
        db.session.add(Dataset(name=name, description=f'{name} dataset description.', data_type=random.choice(["text", "image", "audio", "video"])))

    db.session.commit()

    # Seed Servers
    for _ in range(1000):
        provider = random.choice(server_providers)
        ip_octets = [random.randint(0, 255) for _ in range(4)]
        server_name = f"{provider} Server"
        server_ip = f"{'.'.join(map(str, ip_octets))}"
        db.session.add(Server(name=server_name, ip_address=server_ip))

    db.session.commit()

    # Assuming Version and ModelDeployment require existing Model, Dataset, and Server IDs
    models = Model.query.all()
    datasets = Dataset.query.all()
    servers = Server.query.all()

    # Seed Versions
    for _ in range(1000):
        db.session.add(Version(model_id=random.choice(models).id, dataset_id=random.choice(datasets).id, version_number=f'v{_}.0', performance_metrics='Accuracy: 95%'))

    db.session.commit()

    # Seed ModelDeployments
    for _ in range(1000):
        server = random.choice(servers)
        deployment_time_int = generate_random_date_int(2024, 1, 1, 2024, 3, 25)
        db.session.add(ModelDeployment(server_id=server.id, version_id=random.choice(Version.query.all()).id, deployment_time=deployment_time_int))
    
    db.session.commit()

    print("Database seeded successfully with custom data.")

# Use the app's context when running the script
with app.app_context():
    seed_data()
