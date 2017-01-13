#encoding=utf-8
"""
Process Engine Python API.
fnetpepAPI: version 1.0
copyright: (c) 2016 by Wanderley Souza.
license: Apache2, see LICENSE for more details.
"""

import requests
from requests.auth import HTTPBasicAuth

class PEClient(object):
    
    """Receives a server address, port number, login and password
    for connecting to IBM FileNet Process Engine over IBM's REST API
    and creates the base object for interacting with Process Engine.

    Usage:
    >>> from fnetpepAPI.fnetpepAPI import PEClient, PE
    >>> client = PEClient('server_name', '9080', 'user', 'password')
    >>> client.apps -> PEClient variable with available appspaces
    >>> client.roles -> PEClient variable with available roles
    >>> client.workbaskets.keys()-> Dictionary with available Workbaskets
    >>> client.workflow_classes.keys() -> Dictionary with Workflows.
    """
    
    def __init__(self, server, port, user, passwd):
        self.baseurl = 'http://%s:%s/peengine/P8BPMREST/p8/bpm/v1/'%(server,
                                                                     port)
        self.cred = HTTPBasicAuth(user, passwd)
        self.workbaskets = {}
        self.queue_urls = []
        self.__getAppSpaces()
        self.__getRoles()
        self.__getWorkFlowNames()
        self.__getQueues()

    def __getAppSpaces(self):        
        """Returns a list with the name of availables appspaces on FileNet,
        to apps variable.
        """        
        try:
            appspaces = requests.get(self.baseurl+'appspacenames',
                                     auth=self.cred)
            appspaces.raise_for_status()
            self.appspaces = appspaces.json()            
            self.apps = appspaces.json().keys()
            
        except Exception as e:
            print (str(e)+':\n'+str(appspaces.json()['UserMessage']['Text']))
            print (appspaces.json())
            self.apps =  appspaces.json()
        
    def __getRoles(self):
        """Returns a dictionary with role names and it's queues to a roles
        variable.
        """
        roles = {}
        for a in self.apps:
            url = self.appspaces[a]['rolenames']            
            role = requests.get(self.baseurl+url, auth=self.cred)            
            roles[a] = role.json().keys()
        self.roles = roles
    
    def __getWorkFlowNames(self):
        """Sets all available WorkFlows into workflow_classes variable.
        """
        workflow_names = requests.get(self.baseurl+'workclasses',
                                      auth=self.cred).json()        
        self.workflow_classes = workflow_names 
    
    def __getQueues(self):
        """Creates a list with URL adresses from workbaskets. Also creates a
        dictionary with workbasket name as key and it's URL as value.
        """
        for apps in self.roles.keys():
            for roles in self.roles.values():
                if roles:
                    for role in roles:
                        my_role = requests.get(self.baseurl
                                               +'appspaces/'
                                               +apps+'/roles/'
                                               +role,
                                               auth = self.cred)
                        if my_role.ok:                            
                            for uri in my_role.json()['workbaskets'].values():
                                self.queue_urls.append(uri['URI'])                                
                                self.workbaskets[uri['URI'].split(
                                    '/')[-1]] = uri['URI']
                                
    def getLoggedUserInfo(self):        
        """Returns a dictionary with logged user information.
        Available information are: email, displayName, id and name
        Usage:
        >>> user_info = client.getLoggedUserInfo()
        """
        
        self.userinfo = requests.get(self.baseurl+'currentuser',
                                     auth=self.cred).json()
        return self.userinfo                                

    
class PE(object):
    
    """Creates a PE object. An instance from PEClient must be passed.
    Usage:
    >>> pe = PE(client)
    """
    
    def __init__(self, client):
        self.client = client
        self.apps = client.apps       
        
    def getInboxQueue(self):
        """Returns the User's Inbox Queue.
        Usage:
        >>> inbox = pe.getInboxQueue()
        >>> inbox.get('count') -> Variable with the total tasks in this Queue.
        """        
        work_basket = requests.get(self.client.baseurl+'queues/'
                                        +'Inbox'
                                        +'/workbaskets/'
                                        +'Inbox',
                                        auth = self.client.cred)
        count = requests.get(work_basket.url + '/queueelements/count',
                             auth = self.client.cred).json()['count']
        queue = work_basket.json()        
        queue['count'] = count
        return queue
    
    def getQueue(self, work_basket):
        """Returns a Queue for a given Workbasket.
        Usage:
        >>> my_queue = pe.getQueue('workbasket_name')
        >>> my_queue.get('count')->Variable with the total tasks in this Queue.
        """                
        
        queue = requests.get(self.client.baseurl
                             + self.client.workbaskets.get(work_basket),
                             auth = self.client.cred)
        count = requests.get(queue.url + '/queueelements/count',
                             auth = self.client.cred).json()['count']
        queue = queue.json()
        queue['count'] = count
        return queue

    def getAllTasks(self):
        """Returns all tasks from all Queues.
        Usage:
        >>> tasks = pe.getAllTasks()
        When a Queue has no tasks, a message informing which Queues are empty,
        will be printed.
        """
        tasks = []
        for uri in self.client.queue_urls:
            queue = requests.get(self.client.baseurl + uri,
                                 auth = self.client.cred)
            found_tasks = self.getTasks(queue.json())
            if found_tasks:
                tasks.append(found_tasks)
        return [tsk for task in tasks for tsk in task]

    def getTasks(self, queue):        
        """Returns a dictionary with all tasks for the given queue.
        A queue object is required.
        Usage:
        >>> tasks = pe.getTasks(my_queue)

        """
        work_items = requests.get(self.client.baseurl
                                  + queue.get('queueElements'),
                                  auth = self.client.cred)
        if not work_items.json():
            print ("'%s' queue is empty!"%queue['name'])
        else:
            return work_items.json()['queueElements']

    def getMilestones(self, task):
        milestone = requests.get(self.client.baseurl
                                 + task['milestones'],
                                 auth = self.client.cred)
        return milestone.json()

    def lockTask(self, task):
        
        """Receives a task dictionary, obtainned with getTasks() method,
        and locks the task so other users can't access this task at same time.
        Usage:
        >>> pe.lockTask(task)
        """
        
        locked = requests.get(self.client.baseurl
                              +task['stepElement'],
                              auth = self.client.cred)
        eTag = locked.headers['ETag']
        locked = requests.put(self.client.baseurl
                              + task['stepElement'],
                              auth = self.client.cred,
                              params={'action':'lock',
                                      'If-Match':eTag}
                              )        

    def saveAndUnlockTask(self, task, comment = None):
        
        """Receives a task dictionary obtainned with getTasks() or getAllTasks(),
        method, unlocks the task and saves it. Optionally, is possible to pass
        a comment that will be saved whitin the task.
        Usage:
        >>> task = pe.saveAndUnlockTask(task) or
        >>> task = pe.saveAndUnlockTask(task, "Comment added!!!")            
        """
        
        etag = task['ETag']
        stepEl =  requests.get(self.client.baseurl
                               +task['stepElement'],
                               auth = self.client.cred)
        try:
            if comment:
                updatedJson = stepEl.json()
                updatedJson['systemProperties']['comment'] = comment
                self.lockTask(task)
                unlocked = requests.put(stepEl.url, auth = self.client.cred,
                                        params = {'action':'saveAndUnlock',
                                                  'If-Match':etag},
                                        json = updatedJson)            
            else: 
                unlocked = requests.put(self.client.baseurl
                                        + task['stepElement'],
                                        auth = self.client.cred,
                                        params={'action':'saveAndUnlock',
                                                'If-Match':etag})
            

            for k, v in self.client.workbaskets.items():
                if task.get('queueName') in v:
                    queue = self.getQueue(v.split('/')[-1])
                    tasks = self.getTasks(queue)
                    for newtask in tasks:
                        if newtask['workObjectNumber'] == task['workObjectNumber']:
                            task = newtask
                            break
        except Exception as e:
            self.abort(task)
        return task
    
    def reassignTask(self, task, destination, comment = None):
        
        """This method receives a task and reassigns it to a
        new designated user. The user won't be validated so it must exists
        on the diretory service. It is also possible to create a comment
        before reassigning the task, by using saveAndUnlockTask() method.
        
        Usage:
        >>> pe.reassignTask(task, 'p8_user') or
        >>> pe.reassignTask(task, 'anyuser', "Hey check this out")        
        """
        
        if comment:            
            self.lockTask(task)
            self.saveAndUnlockTask(task, comment)
            
        task = requests.get(self.client.baseurl
                            + task['stepElement'],
                            auth = self.client.cred)
        etag = task.headers['ETag']

        if (task.json()['systemProperties']['canReassign']):
            reassigned = requests.put(task.url, auth=self.client.cred,
                                   params={'action':'reassign',
                                           'participant':destination,
                                           'If-Match':etag})                                
        else:
            return "Task can't be reassigned"
            task.close()

    def getComment(self, task):
        
        """Receives a task and if there is comment, it will be printed.
        Usage:
        >>> comment = pe.getComment(task)
        """
        
        stepelements = requests.get(self.client.baseurl
                                    + task['stepElement'],
                                    auth = self.client.cred)
        comment = stepelements.json()['systemProperties']['comment']

        if comment:            
            return comment

    def getTaskInfo(self, task):
        """Receives a task and invokes __iterDictionary's method
        for printing all information for the given task.
        Usage:
        >>> pe.showTaskinfo(task)
        """
        self.info = {}
        self.__iterDictionary(task)        
        return self.info
        
    def endTask(self, task, comment=None):
        
        """Receives a task and finishes it, finishing the workflow itself.
        Usage:
        >>> pe.endTask(task)
        """        
            
        lock = self.lockTask(task)
        etag = task['ETag']       
        dispatched = requests.put(self.client.baseurl + task['stepElement'],
                                  auth = self.client.cred,
                                  params={'action':'dispatch','If-Match':etag})
    def abort(self, task):
        
        """Receives a task, and unlocks it without saving any changes.
        Usage:
        >>> pe.abort(task)
        """
        
        eTag = task['ETag']
        locked = requests.put(self.client.baseurl+task['stepElement'],
                              auth=self.client.cred,
                              params={'action':'abort',
                                      'If-Match': eTag})
        
    def getAttachmentsInfo(self, task):        
        """Receives a task and prints information about files that has been
        attached to the Workflow.
        Usage:
        >>> pe.getAttachmentsInfo(task)
        """
        self.info = {}
        task = requests.get(self.client.baseurl + task['stepElement'],
                            auth = self.client.cred).json()

        if task['attachments'].keys():
            self.__iterDictionary(task)
            return self.info

    def __iterDictionary(self, dictionary):
        """Receives a dictionary type object and prints all
        it's keys and values.
        """
        for key, value in dictionary.iteritems():            
            if isinstance(value, dict):
              self.__iterDictionary(value)
            else:              
              self.info[key.capitalize()] = value

        
    def startWorkflow(self, **kwargs):
        
        """Starting a new workflow is kind of a complex process,
        since the previously created workflow will determine with data must
        be set before it can be launched. Usually aside data, it is also needed
        or possible to define one or more destination(s) user(s) (that will be
        set for a workflow group) and also attach a document from the
        repository.
        
        By calling this method, issuing only a 'wf_name' attribute, it will
        check if there are fields,workflow groups  and/or document to be
        attached.

        For data fields to be populated, its recommended to check at the
        workflow's configuration, the data type expected for each field
        (integer, string etc) so the data type to be passed here matches
        the data type specified in the workflow.

        To get availables workflow's name, check the workflow_classes's
        variable from PEClient's class: Issue a "help(PEClient)" to know more.

        If a Workflow has at least one 'Document' object, with this API is
        possible to attach documents that are already saved on IBM's FileNet
        repository.
        To do so, the Attachment's name field will be shown when calling
        "startWorkflow" method passing only the 'wf_name' attribute. Then is
        necessary to pass the Attachment's name field and the document ID from
        FileNet. It'll also be required to inform the object store's name.
        
        Usage:
        >>> workclass = wb.startWorkflow(wf_name = 'work_flow_name')
        >>> workclass = wb.startWorkflow(wf_name = 'work_flow_name',
        data_field_name = 'some_value', group_name='users')

        To pass more than one user, write users separated with comma and one
        space, like: 'user1, user2, user3, ..., userX'

        Sample:
        IBM delivers two basic workflow samples with FileNet been:
            "ICNSequentialDocumentApproval and ICNParallelDocumentApproval".            
            Both requires some information, but essencialy only a destinated
            user need to be set.

        To launch the 'ICNSequentialDocumentApproval':

        >>> workclass = wb.startWorkflow(wf_name =
        'ICNSequentialDocumentApproval')

        :To Create this Workflow, you'll probably need to providebelow data:
        :ICN_TeamspaceId
        :ICN_WFDeadlineDate
        :ICN_AllowReassign
        :ReturnToSender
        :ICN_Instructions
        :FinalReview

        :Groups to be populated with users:
        :Approvers

        :Available Attachment Fields:
        :DocumentforReview

        Specifically a "Approvers" group will be used. To finally launch this
        workflow issue the following command:

        >>> workclass = wb.startWorkflow(wf_name =
        'ICNSequentialDocumentApproval', Approvers='user_name')

        Seding a workflow for more than one user:
        >>> workclass = wb.startWorkflow(wf_name =
        'ICNSequentialDocumentApproval', Approvers='user_name1, ..., usernameX')

        Attaching existent document from FileNet:
        >>> workclass = wb.startWorkflow(wf_name='WorkFlow_Name',
        AttachNameField = '{X1111111-1111-XX1X-11XX-XX1X111XX1XX}',
        object_store='ObjectStoreName')

        Launching a workflow providing Data Field, Workflow Group destination
        user and Attachment:
        >>> workclass = wb.startWorkflow(ICN_Instructions='This is Workflow',
        Approvers='user1, ..., userX', object_store='ObjectStoreName',
        DocumentforReview='{X1111111-1111-XX1X-11XX-XX1X111XX1XX}',
        subject = 'New Document For review')

        """
        self.kwargs = kwargs
        wf_name = kwargs.get('wf_name')        
        
        if wf_name not in self.client.workflow_classes:
            return "There's no wf_name key on dictionary or the WorkFlow name\
 doesn't exist."
        work_class = requests.get(self.client.baseurl
                                 + self.client.workflow_classes[wf_name]['URI'],
                                  params={'POE':'1'}, auth=self.client.cred)        
        new_data = work_class.json()
        
        if len(self.kwargs.keys()) <= 1:
            work_class = self.__showAvailableWorkClassOpt(new_data)
        new_data = self.__createNewDataForLaunch(new_data)        
        wobnum = new_data['systemProperties']['workObjectNumber']            

        if len(self.kwargs.keys()) > 1:
            started = requests.post(self.client.baseurl
                                    + 'rosters/DefaultRoster/wc/'
                                    + wf_name+'/wob/'
                                    + wobnum, auth=self.client.cred,
                                    json=new_data, params={'POE':'1'})
            return started
           
        return work_class

    def __showAvailableWorkClassOpt(self, work_class):
        required_data = {}
        """Prints some fields that might be required to be setting
        before sending a Workflow.
        """
        if work_class['dataFields'].keys():
            print ("To Create this Workflow, you'll probably need to provide\
 below data:")
            required_data[
                'Available Data Fields:'] = work_class['dataFields'].keys()
            print ('\n').join(work_class['dataFields'].keys())+'\n'
            
        if work_class['workflowGroups'].keys():
            required_data['Workflow Groups:'
                          ] = work_class['workflowGroups'].keys()
            print("\nGroups to be populated with users:")        
            print ('\n').join(work_class['workflowGroups'].keys())+'\n'

        if work_class['attachments']:
            required_data['Attachments:'] = work_class['attachments'].keys()
            print('\nAvailable Attachment Fields:')
            print ('\n').join(work_class['attachments'].keys())+'\n'

        return required_data

    def __createNewDataForLaunch(self, new_data):
        """Adresses the provided data when calling startWorkflow's method to a
        dictionary to be passed when creating the workflow.
        """
        if new_data['workflowGroups'].keys():            
            for group in new_data['workflowGroups'].keys():
                if self.kwargs.get(group):
                    new_data['workflowGroups'][group][
                        'value'] = self.kwargs.get(group).split(', ')
                    
        if new_data['dataFields'].keys():            
            for data_field in new_data['dataFields'].keys():
                if self.kwargs.get(data_field):
                    new_data['dataFields'][data_field][
                        'value'] = self.kwargs.get(data_field)

        subject = self.kwargs.get('subject')
        if subject:
            new_data['systemProperties']['subject'] = subject

        if new_data['attachments']:
            for attachment in new_data['attachments'].keys():
                if self.kwargs.get(
                    attachment) and self.kwargs.get('object_store'):
                    
                    d_id = self.kwargs.get(attachment)
                    object_store = self.kwargs.get('object_store')
                    document = {u'title':'Attachment',
                                u'libraryType':3,
                                u'libraryName':object_store,
                                u'vsId':d_id,
                                u'version':d_id,
                                u'type':3,
                                u'desc':u''}                    
                    new_data['attachments'][attachment][
                        'value'] = document 
        return new_data
