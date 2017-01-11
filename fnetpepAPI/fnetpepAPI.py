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
    
    """Receives a server address, port number, login
    and password for connecting to IBM FileNet
    Process Engine over IBM's REST API and creates an object.

    Usage:
    >>> from pythonPERest import PEClient, WorkBasket
    >>> client = PEClient('server_name', '9080', 'user', 'password')
    >>> client.apps -> Shows available appspaces
    >>> client.roles -> Shows available roles
    >>> client.workflow_classes.keys() -> Show available Workflow
    """
    
    def __init__(self, server, port, user, passwd):
        self.baseurl = 'http://%s:%s/peengine/P8BPMREST/p8/bpm/v1/'%(server,
                                                                     port)
        self.server = server
        self.cred = HTTPBasicAuth(user, passwd)
        self.__getAppSpaces()
        self.__getRoles()
        self.__getWorkFlowNames()        
        self.queue_names = self.roles.values()        

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

    def getLoggedUserInfo(self):
        
        """Returns a dictionary with logged user information.
        Available information are: email, displayName, id and name
        """
        
        self.userinfo = requests.get(self.baseurl+'currentuser',
                                     auth=self.cred)        
        return self.userinfo.json()

    
class WorkBasket(object):
    
    """Create a WorkBasket object. Must pass a PEClient instance.
    If a 'queue_name' is not specified, the 'Inbox' work basket will be returned.
    To see availlable 'queues', run client.queue_names.
    
    Usage:
    >>> wb = WorkBasket(client, 'queue_name')
    """
    
    def __init__(self, client, queue_name='Inbox'):
        self.client = client
        self.apps = client.apps
        self.url = None
        self.queue = queue_name
        self.work_basket = self.__getQueueFromRole()
        self.properties = self.__getWorkBasketProps()
        
    def __getWorkBasketProps(self):
        """Returns properties from a work basket to a class variable.
        """
        properties = requests.get(self.client.baseurl+'queues/'
                                  + self.queue
                                  +'/workbaskets/'
                                  +self.queue
                                  +'/columns',
                                  auth = self.client.cred)
        return properties.json()
        
        
    def __getQueueFromRole(self):
        """Returns Queues from a Role.
        """        
        self.work_basket = requests.get(self.client.baseurl+'queues/'
                                        + self.queue
                                        +'/workbaskets/'
                                        +self.queue,
                                        auth = self.client.cred)
        self.url = self.work_basket.url
        self.queue_url = self.work_basket.json()['queueElements']
        return self.work_basket.json()
    
    def getElementsCount(self):
        
        """Returns the amount of available tasks for the queue
        returned in getQueueFromRole method        
        """
        
        count = requests.get(self.url+'/queueelements/count',
                             auth=self.client.cred)
        return count.json()['count']

    def getTasks(self):
        
        """Returns a dictionary with all tasks for the given queue.
        If there aren't tasks, 'None' will be returned.
        """
        
        work_items = requests.get(self.client.baseurl + self.queue_url,
                                  auth = self.client.cred)
        if not work_items.json():
            print ("'%s' queue is empty!"%self.queue)
            return None
        tasks = work_items.json()['queueElements']
        return tasks

    def getMilestones(self, task):
        milestone = requests.get(self.client.baseurl
                                 + task['milestones'],
                                 auth = self.client.cred)
        return milestone.json()

    def lockTask(self, task):
        
        """Receives a task dictionary, obtainned with getTasks() method,
        and locks the task so other users can't access this task at same time.
        Usage:
        >>> wb.lockTask(task)
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
        
        """Receives a task dictionary obtainned with getTasks() method,
        unlocks the task and saves it.
        Optionally, is possible to pass a comment that will be saved in
        the task.
        Usage:
        >>> wb.saveAndUnlockTask(task) or
        >>> wb.saveAndUnlockTask(task, "Comment added!!!")            
        """
        
        etag = task['ETag']
        stepEl =  requests.get(self.client.baseurl
                               +task['stepElement'],
                               auth = self.client.cred)
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
    
    def reassignTask(self, task, destination, comment = None):
        
        """This method receives a task and reassigns it to a
        new designated user. The user won't be validated so it must exists
        on the diretory service. It is also possible to create a comment
        before reassigning the task, by using saveAndUnlockTask() method.
        
        Usage:
        >>> wb.reassignTask(task, 'p8_user') or
        >>> wb.reassignTask(task, 'anyuser', "Hey check this out")        
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
            print("Task can't be reassigned")
            task.close()

    def showComment(self, task):
        
        """Receives a task and if there is comment, it will be printed.
        Usage:
        >>> wb.showComment(task)
        """
        
        stepelements = requests.get(self.client.baseurl
                                    + task['stepElement'],
                                    auth = self.client.cred)
        comment = stepelements.json()['systemProperties']['comment']

        if comment:
            print (comment)

    def showTaskInfo(self, task):

        """Receives a task and invokes __printDictionary's method
        for printing all information for the given task.
        Usage:
        >>> wb.showTaskinfo(task)
        """
        
        task = requests.get(self.client.baseurl+task['stepElement'],
                            auth=self.client.cred).json()
        self.__printDictionary(task)                    
        
    def endTask(self, task):
        
        """Receives a task and finishes it, finishing the workflow itself.
        Usage:
        >>> wb.endTask(task)
        """
        
        lock = self.lockTask(task)
        etag = task['ETag']       
        dispatched = requests.put(self.client.baseurl + task['stepElement'],
                                  auth = self.client.cred,
                                  params={'action':'dispatch','If-Match':etag})
    def abort(self, task):
        
        """Receives a task, and unlocks it without saving any changes.
        Usage:
        >>> wb.abort(task)
        """
        
        eTag = task['ETag']
        locked = requests.put(self.client.baseurl+task['stepElement'],
                              auth=self.client.cred,
                              params={'action':'abort',
                                      'If-Match': eTag})
    def showAttachmentsInfo(self, task):
        
        """Receives a task and prints information about files that has been
        attached to the Workflow.
        """
        
        task = requests.get(self.client.baseurl + task['stepElement'],
                            auth = self.client.cred).json()
        
        if task['attachments'].keys():
            self.__printDictionary(task)

    def __printDictionary(self, dictionary):
        """Receives a dictionary type object and prints all
        it's keys and values.
        """
        for key, value in dictionary.iteritems():            
            if isinstance(value, dict):
              self.__printDictionary(value)
            else:
              print "{0} : {1}".format(key.capitalize(), value)
        print ('\n')

    
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
