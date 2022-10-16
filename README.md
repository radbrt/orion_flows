# Moving from Prefect 1 to Prefect 2

A lot of people have to port their workflows from prefect 1 to prefect 2. After spending way too long to get Prefect 2 up and running, I am now finally able to start converting my flows. Most of this post will be about things other than Prefect code though - like getting Azure set up in a meaningful way.

1. Creating an AKS cluster and starting the agent
2. Connecting storage
3. Connecting a Key Vault
4. Converting flows
5. Create a queue

## Creating an AKS cluster
If you have prefect 1 up and running, you probably know this part. If not I'll give you the cliffnotes version, using the Azure CLI. Don't worry, I'm a fan of click-ops, and we'll get into the portal soon enough.

First off, you probably want a resource group to for all the azure resources we are going to spin up. Let's call it **orion**. And because I'm in Europe, I feel like placing it in the west-europe region. We are also setting our default location to west europe, and our default resource group to the newly created "orion" group, which will simplify some of the later commands. 

`az configure --defaults location=westeurope`
`az group create --name orion`
`az configure --defaults group=orion`

If you prefer not to set these defaults, you can add `--resource-group orion --location westeurope` to the commands below.

`az aks create --name prefectkube --node-count 1 --enable-addons monitoring --generate-ssh-keys --location westeurope --enable-managed-identity`

Note that we enable managed identity. The Azure access management universe is somewhat complicated, but for our purposes now we'll say that we use Managed Identity for access management for all our resources. The alternative is to use Service Principals. I'm not saying one approach is better than the other (the default is to use service principals), but Managed Identity is what I know and can explain.

Once this is up and running, you need to authenticate with it through `az aks get-credentials`. This will add the cluster to your `~/.kube/config` file. The last thing we need to do now is to make sure the new AKS cluster is the default cluster your `kubectl` program uses: `kubectl config use-context prefectkube`.

In order to get the agent up and running, we need at least two things: Our workspace URL, and our API Key. These can both be found in the Prefect 2 UI, and Laura does a better job of explaining where to find them than I do. For now, we'll pretend our workspace URL is `https://api.prefect.cloud/api/accounts/api/accounts/19f6a4c7-c2f3-4d96-8c51-5fbae707fc57/workspaces/49231bd0-c4ff-4829-9834-b42908910ab6` and our API Key is `pnu_18d2d570Ab2beB482eD9947Ed5c2d284619c`. To be clear, these ones are entirely made up, but the format is fairly correct.

You will see a lot of somewhat different deployment specifications, this one includes what I think of as a few good practices, without getting too complicated. Basically, the deployment uses the URL and API Key, but we don't want to reference them in plaintext. Instead, we create kubernetes secrets first, and reference them in the deploy script.


```sh
kubectl create secret generic prefect \
--from-literal=api-url='https://api.prefect.cloud/api/accounts/19f6a4c7-c2f3-4d96-8c51-5fbae707fc57/workspaces/49231bd0-c4ff-4829-9834-b42908910ab6' \
--from-literal=api-key='pnu_18d2d570Ab2beB482eD9947Ed5c2d284619c'
```

If you are unfamiliar with kubernetes secrets, it might help to retrieve it, and see what it looks like: `kubectl get secret prefect -o jsonpath='{.data}'`. It is basically a JSON dictionary, with a key for the URL, and a key for the API Key.

The YAML deployment script references these secrets, so you don't need to store them in the script.

One last thing: The agent connects to a queue named "kubernetes", which you will have to create in the Prefect UI. All jobs have to be picked up by a queue in order to run on schedule or get triggered, but we have not yet created that queue. We'll get back to that.

For now, we can deploy the agent by running `kubectl apply -f agent.yaml`.

## Create and connect storage

When running in Azure, it is natural to store our flows in Azure Blob storage. We need to give our AKS cluster access to the storage blob, which is probably easier to do in the portal. Just search for "Storage Accounts" and choose "Create", give it a name, choose our "orion" resource group, and you can use the defaults for the rest.

After it is created, go to the resource and in the sidebar you will find "Access Control (IAM)". Click it, and at the top click the "+ Add" button and "Add role assignment". Find the "Storage Blob Data Reader" role. On the "Members" tab, choose to assign access to "Managed Identity", and select members. In the "Managed Identity" dropdown select "Kubernetes Service", and you will probably see your AKS Cluster. Select it, click the "Select" button at the bottom, and "Review + assign". Now, the AKS Cluster should have access to read data from the storage blob. While we are here, we need to create a container to store the flows in, and pick up the access keys for the storage account.

To create a container, select "containers" in the sidebar (under the "Data storage" section), choose "+ Container", and give it a name. You will need this name in a second.

The access keys are also important, you will find them under "Access keys" in the sidebar (under the "Security and networking" section). What you want to copy is the "Connection string" value from Key 1 (there are two keys so that you will be able to rotate one key at the time). It should start with `DefaultEndpointsProtocol=https;AccountName=<...>`. Again, we will need this in a second.


## Connect a Key Vault

Depending on what you want to do in Prefect, you might not need a Key Vault. And Prefect 2 Secrets is just around the corner, so if you can wait a little that will be an option. But lots of people prefer using Azure Key Vault, perhaps as a company policy. 

Creating a Key Vault is simple, and you enable access to it from the AKS cluster just like with the storage account, by going into "Access Control (IAM) in the sidebar, add a new access assignment, find the "Key Vault Secrets User" role, and add it to the AKS Cluster Managed Identity just like you did with the storage account.

PS: Aazure will happily create a good number of identities for the AKS cluster. AKS will pop up as one identity, the Virtual machine scale set (VMSS) that the cluster runs on will pop up, as well will a used-assigned managed identity. While the storage was happy when we assigned access rights to the AKS identity, the trick when using Python to access Key Vault seemed to be to assign the reader role to the ID of the Virtual machine scale set. I'm not sure I got that right.

## Convert the flows

Now that Prefect 2 (previously Orion) is GA, it has some features I have been waiting for. Importantly, Blocks. Especially because we use Secrets in Prefect 1, blocks (of type Secret) is perfect.

## Create a queue, deploy, and run
Lastly, we need to create a work queue. We hinted at this in the first part, we already created an agent that looks for a queue named "kubernetes" so we should really create a queue like that. This queue can be created very simply on the command line: `prefect work-queue create kubernetes`. Actually, you don't even have to anymore. Recent versions of prefect creates these queues automatically when creating a deployment.

Now, if all has gone well, you can register the flow with Prefect Cloud by running `prefect deployment create orion_flows/dn_flow/flow.py`. Hopefully needless to say, that flow points to my own stuff in GCP etc, so don't just copy-paste that flow. Replace the inner workings of it with something else.

With that last piece of formality done, you can go into the Prefect UI, under "flows" in the left meny you will hopefully find your flow. If you click it, you will see some more details about it, and a "quick run" button. Click, and check the "Flow Runs" tab to find your fresh run.

## CI/CD Deployments

We want to create deployments from flows, and we have two main requirements:
- Several deployments per flow, so that we can have different schedules, different arguments, etc.
- We want to specify image name, storage etc in the deployment, for flexibility.


We satisfy these requirements by having separate Deployment files. Any file ending in `deployment.py` will be found and run by the CI/CD process (github action). Inside this file, we import the flow function, create a Deployment object and run the `apply()` method on it so that it gets registered with Prefect.

These deployment files can also be run locally, as long as the user is logged in to prefect cloud.