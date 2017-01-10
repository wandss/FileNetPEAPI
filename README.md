# FileNetPEAPI
A Python API for using FileNet Process Engine (Case Foundation)
Package name: fnetpepAPI

This document explains how to use this API.
Is important to have some knowledge on some Process Engine concepts like:
**Queues, Roles, Workbaskets, etc.**

Obviously knowing Python will help.

This API requires [Requests](https://github.com/kennethreitz/requests) by Kenneth Reitz, so install it before.

###Running the API:
```python
from pepa import PEClient, WorkBasket
```
###To create a "connection":
```python
client = PECLient('server_name', 'server_port', 'user', 'passwd')
```
**Sample:**
*client = PEClient('content_engine', '9080', 'p8admin', 'password')*
With This client instance of PEClient  you can check:

####Available App Spaces:
*Prints appspace names*
```python
client.apps
```
####Available Queues:
*Prints a list with queue_names.*
```python
client.queue_names
```
####Available Roles:
*Prints available roles*
```python
client.roles
```
####Available Workflow:
*Prints available workflow names*
```python
client.workflow_classes.keys()
```
###Now, create a Workbasket object:
To do so, is required to pass an **instance from PEClient** and a **queue name**.
The available queues can be obtained as shown above.
*If no queue_name is passed, the program will inspect the **‘Inbox’** for the connected user.*
```python
wb = WorkBasket(client)
```
or
```python
wb = WorkBasket(client, 'Queue_name')
```
###With a WorkBasket object is possible to retrieve information from a workbasket:

*Prints the url for the workbasket that is been used.*
```python
wb.url
```
*Prints all the tasks available in the Queue for the given workbasket:*
```python
wb.getElementsCount()
```
*Get all the tasks from this queue:*
```python
tasks = wb.getTasks()
```
*Above, a python list object with tasks will be returned.
Each task inside this list, is a python dictionary object.*

###Tasks are the final objects from a Queue. Is possible to interact with them and do the following actions:
- Reassign the task to other user, 
- Add a comment, 
- Locks it, so other users can’t interact while you're working with it, 
- Unlocks the task without saving any modifications, 
- Show comments, 
- Show information from a task, 
- Show information from documents attached to a the task.

####Showing information from tasks:
*You can iterate tasks:*
```python
for task in tasks:      
      wb.showTaskInfo(task)
```            
*Or work with a specific task*:
```python
task = tasks[0]
```
*Showing Information for a task:*
```python
wb.showTaskInfo(task)
```
*Showing Comments for a task:*
```python
wb.showComment (task)
```
*Showing AttachmentsInfo for a task:*
```python
wb.showAttachmentsInfo (task)
```
###Reassigning a task:
*To reassign a task, a destination user must be informed:*
```python
wb.reassignTask(task, 'new_user')
```
*It is also possible to add a comment like:*
```python
wb.reassignTask(task, 'new_user', 'Hello. This document needs your attention')
```
*In case you want to add a comment but not reassign a task, issue:*
```python
wb.saveAndUnlockTask(task, 'Check this out later')
```
*When interacting with a task it will automatically be locked, so you might need to unlocks it by issuing:*
```python
wb.abort(task)
```
##Starting (Launching) a new Workflow:
Starting (launching) a worflow could be a little complex since each workflow is created with specific needs and configuration.
Is possible to have a workflow that needs to set a destination user and others that already has a specified destinated user.
Sometimes, when creating a workflow you might have to determine some datafields to be filled in at launch step or having the option to attach documents. Many possibilities here.

So, since it Workflow has its needs, the first thing is to understand what are the needs from that workflow, to do this run:
```python
launchstep = wb.startWorkflow(wf_name = 'WorkFlowName')
```
*You must run this with the wf_name property, not doing so, will return the message:
**"There's no wf_name key on dictionary"***
To find out Workflow names issue (as mentioned above):
```python
client.workflow_classes.keys()
```
After properly issuing the above command, depending on the workflow,the options to be printed out can be:
- Data Fields Names
- Workflow groups Names
- Attachment Name Field

Usually IBM packages two basic Document Approval sample workflows:
- ICNSequentialDocumentApproval,
- ICNParallelDocumentApproval

###Let's use one of them as example:
*When running:*
```python
wb.startWorkflow(wf_name='ICNSequentialDocumentApproval')
```
*The result would be*:
```
To Create this Workflow, you'll probably need to provide below data:
ICN_TeamspaceId
ICN_WFDeadlineDate
ICN_AllowReassign
ReturnToSender
ICN_Instructions
FinalReview

Groups to be populated with users:
Approvers

Available Attachment Fields:
DocumentforReview

```
**Explaining above info:**
```
- ICN_TeamspaceId
- ICN_WFDeadlineDate
- ICN_AllowReassign
- ReturnToSender
- ICN_Instructions
- FinalReview
```
*These are data fields availabe for the workflow. It doesn't mean that all of this data fields must be provided. It will depends on how the worflow was written, but this shows which data fields exists on this particular Workflow.*

```
- Approvers
```
*This is a group to be populated with one or many users.*
```
- DocumentforReview
```
*Finally, this is the field to be used when attaching a document.*

###Samples to starting this workflow we could be:
####Sending to one user:
```python
launched = wb.startWorkflow(wf_name='ICNSequentialDocumentApproval', Approvers='destinated_user' )
```
*Only informed one destination user.*
####Sending to more users:
```python
launched = wb.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2' )
```
*To send for more than one user, write user_names separated by ', ' comma and space like:
**Approvers = 'user1, user2, ..., userX'***

####Setting users and values for data field:
```python
launched = wb.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2',
                            ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True                            
                            )
```
***When using Data Fields, the type passed for the value here must match the type written in workflow.
In the above example "ICN_AllowReassign" was created in workflow as a boolean type, so here we must matchs the same type by passing
True and not 'True'***

####Setting users, values for data field and attaching a document:
```python
launched = wb.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2', ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True, DocumentforReview='{Filenet's Document ID}',
                            object_store='ObjectStoreName', subject="New Document for review"
                            )
```
***Only documents available in FileNet repository can be attached, therefore the ID for this document must be passed here. It is also required to pass the object_store key with the desired 'ObjectStoreName'
It is also possible to set a subject for this Workflow by passing the parameter: subject with any string you like as value.***

As shown in this part above, starting (lauching) a workflow relies on many variables. Therefore is important to know the workflow that's been started.

###Commum atributes for any workflows are:
- wf_name
- subject
Any other attribute depends for the workflow.

##Notes on this program:
Obviously there are many things to improve at this API (and maybe some bugs) yet, at the state it is now, I do believe it can be shared since I've used it to implement at least trhee other applications and they are working just fine.

I do hope this API can be useful for those who intends to develop FileNet application.
