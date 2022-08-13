# Reading from snowflake with dask-snowflake

There are plenty of ways to interact with databases in Python. Sqlalchemy has become a de-facto standard for creating connections, and pandas has an easy method for reading from databases.

Reading data from SQL databases into a distributed framework is a lot more difficult. Although databases can easily parallelize its computations, the results are read from a single connection and making sure it doesn't end up in a single partition is difficult.

The dask-snowflake library fixes this, and can read natively read data from snowflake into a distributed dask dataframe. There is no need to specify partition columns - snowflake handles it automatically, giving dask a good starting point for distributed computation in python.

Without distributed SQL reads, loading data from snowflake into dask would be a multi-step process. In order to read in parallel, you would need to start by dumping the data out of snowflake and into cloud storage. This works because snowflake splits data into blocks, by default 32MB in size.

And in order to dump data to cloud storage, you will need to create a snowflake stage - which requires you to supply credentials for the storage account so that snowflake can write to it.

This is getting complicated:
1. Obtain storage credentials
2. create a snowflake stage
3. Copy data into the snowflake stage, which results in the data being written to cloud storage
4. Read the data from cloud storage (which again requires authentication)

Not only is this a hassle, it is also a security liability.

The alternative is a lot simpler

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

