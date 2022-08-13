# Reading from snowflake with dask-snowflake

There are plenty of ways to interact with databases in Python. Sqlalchemy has become a de-facto standard for creating connections, and pandas has an easy method for reading from databases.

Reading data from SQL databases into a distributed framework is a lot more difficult. Although databases can easily parallelize its computations, the results are read from a single connection and making sure it doesn't end up in a single partition is difficult.

The dask-snowflake library fixes this, and can read natively read data from snowflake into a distributed dask dataframe. There is no need to specify partition columns - snowflake handles it automatically, giving dask a good starting point for distributed computation in python.

## How to load data without dask-snowflake

Without distributed SQL reads, loading data from snowflake into dask would be a multi-step process. In order to read in parallel, you would need to start by dumping the data out of snowflake and into cloud storage. This works because snowflake splits data into blocks, by default 32MB in size.

And in order to dump data to cloud storage, you will need to create a snowflake stage - which requires you to supply credentials for the storage account so that snowflake can write to it.

This is getting complicated:
1. Obtain storage credentials
2. create a snowflake stage
3. Copy data into the snowflake stage, which results in the data being written to cloud storage
4. Read the data from cloud storage (which again requires authentication)

Not only is this a hassle, it is also a security liability.

### Obtain storage credentials

If you are on Azure (like me), snowflake lets you connect a storage account by using storage a storage principal. If you need a general purpose stage for some time to come, this is definetely what you should do. If you only need to write to the stage, it might be better to create the stage with a SAS key. Why? Because all you need to do is write. SAS tokens lets you specify write-only permissions, while using a service principal it is not possible to grant write permissions without also granting read permissions.

You could, of course, create a SAS key that is valid for the foreseeable future, but security people frown at that. Generally, keys should be short-lived and rotated frequently. Luckily, Prefect lets us automate the process, generating a new short-lived SAS token and replacing the share on whatever cadence you are comfortable with. Check the flow under `warehouse/renew_stage` to see how it's done. Or, you could just use dask-snowflake.

### Create a snowflake stage

OK this is one simple SQL command in snowflake, how hard can that be?

Well, before you can create a stage you need to create a file format - after all, the data dumped needs to be in some data format.  As data-savvy people parquet is the go-to option, but beware. When dumping to parquet, snowflake does not care to bring the column names with it. All the columns have genreic names, col0, col1, etc. Oh, and Parquet doesn't handle certain timestamp formats, resulting in an error. So perhaps you want to use CSV, but then you loose even column types. A decent compromise is to use the JSON format, but the drawback is that you have to pack your queries into a `object_construct_keep_null(*)` query that packs each row into a json object. Dumping this results in so-called newline-delimited json which can be read without much trouble.

So OK, once you have settled on the file format, you can create the stage. Just decide on a database and schema to put it. And make sure the user that creates the stage actually has permissions to create it, and the relevant users has access to it. And to the file format. Creating the file format and stage is done in the `warehouse/renew_stage` flow. Or, you could just use dask-snowflake.

### Copy data into the snowflake stage

So you have the stage ready to go, the credentials rotates automatically and the security group is happy. Although not as happy as they would have been if you had used dask-snowflake and didn't have a need for the storage account at all. But none the less. Automatically rotating access keys makes you look 1337.

So you are ready to query some data, and you want to do a query like `select first_name, last_name, zip_code, start_date FROM customers`. Because you copy the data into json, you need to wrap the query so that the real query looks something like this:

```sql
COPY INTO @my_db.my_schema.my_stage/my_storage_folder FROM (
    SELECT object_construct_keep_null(*) FROM (
        select first_name, last_name, zip_code, start_date FROM customers
    )
)
```

And make sure you remember the name of the storage folder you wrote to. This needs to be unique, and is where the json files ends up. Or, you could just use dask-snowflake.


### Read the files from storage

So this is easy, just a normal dd.read_json() call and you're ready. Snowflake has partitioned your data nicely for you in chunks that don't exceed 32MB (unless you have specified something else), and at least as many files as your warehouse has threads.

```py

import dask.dataframe as dd

CONTAINER='work'
FOLDER = 'dask_json_folder'
ACCOUNT_NAME = 'my-storage-account'
az_creds = DefaultAzureCredential()
account_key = get_my_account_key(az_creds, CONTAINER, FOLDER, ACCOUNT_NAME)

jdf = dd.read_json(
    f"abfs://{CONTAINER}/{FOLDER}/*.json", 
    lines=True, 
    orient="records",
    storage_options={
        'account_name': ACCOUNT_NAME, 
        'account_key': account_key
    }
)
```

OK there's the authentication thing. The homemade `get_my_account_key` utility function abstracts away some weirdness. See, usually the way to authenticate with azure is to create a `DefaultAzureCredential` object and pass it into whatever azure sdk thing you are using. Here though, you need to pass in an actual storage account key in the form of a string. No, it's not pretty. But the good news is that we can repurpose some code we have already written in the `warehouse/renew_stage` flow. Let's take a look at it:

```py
def get_my_account_key(az_creds, CONTAINER, FOLDER, ACCOUNT_NAME):
    subscription_id = '<subscription_id>'
    RESOURCE_GROUP_NAME = '<rg_name>'
    creds = DefaultAzureCredential()
    bsc = BlobServiceClient(
        account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net/", 
        credential=az_creds
    )

    smc = StorageManagementClient(az_creds, subscription_id=subscription_id)
    account_keys = smc.storage_accounts.list_keys(resource_group_name=RESOURCE_GROUP_NAME, account_name=ACCOUNT_NAME)

    return account_keys.keys[0].value
```

See, it's not so bad. OK, you need to find the resource group name in which the storage account is located, and your Azure subscription ID which is one of those **not a secret but kind of a secret* things. But with that, you have successfully read your snowflake data into a dask dataframe. Or, you could just use dask-snowflake.


## How to use dask-snowflake

So with that baseline ready, here's how it could be done instead:

1. Import read_snowflake and run the query
2. That's it. Done.

```py
from dask_snowflake import read_snowflake


example_query = f"""
    select *
    from {db}.{schema}.{table_name};
"""

ddf = read_snowflake(
        query=example_query,
        connection_kwargs={
            "user": username,
            "password": password,
            "account": account,
            "warehouse": warehouse
        }
    )
```


No storage blobs to manage, no storage credentials, no stages, no key rotation, no subscription ID or resource group name.


