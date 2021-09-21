
# CDK Sample: Deploy a Hugging Face Transformer model to Amazon Sagemaker

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.


Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

snippet

```bash

# clone repository
git clone https://github.com/philschmid/sample-huggi

# install 
pip3 install -r requirmenets

# bootstrap 
cdk bootstrap

# deploy
cdk deploy --parameters model=distilbert-base-uncased-finetuned-sst-2-english --parameters task=text-classification --profile hf-sm
cdk synth --parameters model=distilbert-base-uncased-finetuned-sst-2-english --parameters task=text-classification --profile hf-sm > deploy.yaml

