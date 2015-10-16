import logging
from flask import Flask, render_template, json, request
from v1pysdk import V1Meta

DEV_TASK_NAME = 'Development'
AUTOMATED_TESTING_TASK_NAME = 'Automated Testing'
TESTING_TASK_NAME = 'Testing'
CODE_REVIEW_TASK_NAME = 'Code Review'
DOCUMENTATION_TASK_NAME = 'Documentation'
TESTING_REVIEW_TASK_NAME = 'Test Case Review'
DOCUMENTATION_REVIEW_TASK_NAME = 'Documentation Review'

DEV_TASK_TODO = 5
AUTOMATED_TESTING_TASK_TODO = 1
TESTING_TASK_TODO = 5
CODE_REVIEW_TASK_TODO = 1
DOCUMENTATION_TASK_TODO = 5
TESTING_REVIEW_TASK_TODO = 1
DOCUMENTATION_REVIEW_TASK_TODO = 1

CODE = "TaskCategory:112";
DOCUMENTATION = "TaskCategory:493515";
TEST = "TaskCategory:538305";
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TC')

def deleteAssetTasks(usr, pwd, assets):
    with V1Meta (instance_url = 'https://www11.v1host.com/VentyxProd', username = usr, password = pwd) as v1:
        for asset in assets.split(','):
            if asset.startswith('B'):
                parentType = "Story"
                parent = v1.Story.where(Number=asset).first()
            else:
                parentType = "Defect"
                parent = v1.Defect.where(Number=asset).first()
            oidToken = parentType+":"+parent._v1_oid
            tasks = v1.Task.where(Parent = oidToken)
            for task in tasks:
                task.Delete()
        v1.commit()
    return assets

def createAssetTasks(usr, pwd, assets):
    with V1Meta (instance_url = 'https://www11.v1host.com/VentyxProd', username = usr, password = pwd) as v1:
        for asset in assets.split(','):
            if asset.startswith('B'):
                parent = v1.Story.where(Number=asset).first()
                test_case_review_task = v1.Task.create(Name = TESTING_REVIEW_TASK_NAME, Parent = parent, ToDo = TESTING_REVIEW_TASK_TODO, Category = TEST)
                documentation_task = v1.Task.create(Name = DOCUMENTATION_TASK_NAME, Parent = parent, ToDo = DOCUMENTATION_TASK_TODO, Category = DOCUMENTATION)
                documentation_review_task = v1.Task.create(Name = DOCUMENTATION_REVIEW_TASK_NAME, Parent = parent, ToDo = DOCUMENTATION_REVIEW_TASK_TODO, Category = DOCUMENTATION)
            else:
                parent = v1.Defect.where(Number=asset).first()
                dev_task = v1.Task.create(Name = DEV_TASK_NAME, Parent = parent, ToDo = DEV_TASK_TODO, Category = CODE)
                dev_task.QuickSignup()
                service_test_task = v1.Task.create(Name = AUTOMATED_TESTING_TASK_NAME, Parent = parent, ToDo = AUTOMATED_TESTING_TASK_TODO, Category = CODE)
                service_test_task.QuickSignup()
                code_review_task = v1.Task.create(Name = CODE_REVIEW_TASK_NAME, Parent = parent, ToDo = CODE_REVIEW_TASK_TODO, Category = CODE)
                code_review_task.QuickSignup()
                qa_task = v1.Task.create(Name = TESTING_TASK_NAME, Parent = parent, ToDo = TESTING_TASK_TODO, Category = TEST)
    return assets

def getAssetsWithoutTasks(usr, pwd):
    with V1Meta (instance_url = 'https://www11.v1host.com/VentyxProd', username = usr, password = pwd) as v1:
        assets=[x.Number for x in filter (lambda x: x.Number.startswith(('B-','D-')),  v1.Member.select('OwnedWorkitems.Number').where(Username=usr).first().OwnedWorkitems)]
        stories=['Number="'+x+'"' for x in filter (lambda x: x.startswith('B'),assets)]
        defects=['Number="'+x+'"' for x in filter (lambda x: x.startswith('D'),assets)]

def createAllAssetTasks(usr, pwd):
    return ""

@app.route('/')
def main():
    return render_template('process.html')

@app.route('/process',methods=['POST','GET'])
def process():
    _assets = request.form['inputAsset']
    _user = request.form['inputUser']
    _password = request.form['inputPassword']
    _action = request.form['action']
    logger.info('Processing [%s] with [%s]-[%s]', _action, _user, _assets)
    if _user and _password and (_assets or _action == 'CreateAll'):
        if _action == 'Delete':
            logger.info('Deleting tasks for [%s]', _assets)
            result = deleteAssetTasks(usr=_user, pwd=_password, assets=_assets)
            _message = 'Deleted tasks for '+_assets
            logger.info('Message: %s', _message)
        elif _action == 'Create':
            logger.info('Creating tasks for [%s]', _assets)
            createAssetTasks(usr=_user, pwd=_password, assets=_assets)
            _message = 'Created tasks for '+_assets
        else:
            logger.info('Creating tasks for all empty assets')
            createAllAssetTasks(usr=_user, pwd=_password)
            _message = 'Created all tasks for '+_assets
    logger.info('Finishing [%s]', _action)
    return render_template('process.html', message = _message)

if __name__ == "__main__":
    logger.info('Starting')
    app.run(host='0.0.0.0')
