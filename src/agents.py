from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from .database import sql_db
from .ai_model import llm


sql_agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=sql_db, llm=llm),
    verbose=True
)
