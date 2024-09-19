db_information = '''
        1. Album- Gives the infomration about Albums.(Id, Name of the album and id of the artist who created the album)
        2. Artist- Gives the information about the Artist. (Id and Name of the artist)
        3. Customer- Gives the personal information about the Customers. (Id and their personal details like name, address, etc.)
        4. Employee- Gives the personal information about the Employees. (Id, personal details like name, title of their role, id of the employee whom should they report to, birthday, hiring date, address, etc.)
        5. Genre- Gives the information about the Genre of the Track(Id and Name of the Genre)
        6. Invoice- Gives the customer's billing information about the sale. (Id, id of the customer who bought that, the date of purchase, the total amount for that purchase, billing address, etc.)
        7. InvoiceLine- Gives the information about the product of sale. (Id, id of the invoice, id of the track they bought, unit price for each track and the quantity they bought)
        8. MediaType- Gives the names of the type of the media. (Id and name)
        9. Playlist- Gives the names of the playlists. (Id and name)
        10. PlaylistTrack- Gives the information about the playlist's tracks(Id of the playlist and id of the track)
        11. Track- Gives the information about the track. (Id, name of the track, id of the album, mediatype, and genre, name of the composer of the track, duration of the track in milliseconds, size of the track in bytes, and unit price for each track track)
    '''

sql_generation_template = """
        You will be provided with a question. Your task is to analyze the schema provided and generate an SQL query \
        which can be used to query the result from the database. The schema will give the name of the tables and columns. \
        The complete information about the database columns will be given below along with the instructions. \
        The answer should be adhere to the instructions given below.
        Question: {question} \
        Database Schema: {schema} \
        Table and Columns Information: {db_info} \
        Instructions: {instructions}
    """

sql_generation_with_history_template = """
        You will be provided with a question. Your task is to analyze the schema provided and generate an SQL query which should be\
        case insensitive using ILIKE which can be used to query the result from the database. Check the history of the chat for better understanding\
        of the chat and if the history helps in generating the answer without querying please provide that instead of the query.\
        The schema will give the name of all the tables and columns.The information about the\
        tables and columns that should be used for the task will be given below along with the instructions.\
        The answer should be adhere to the instructions given below. \n
        History: {history}
        Database Schema: {schema} \n
        Table and Columns Information: {db_info} \n
        Instructions: {instructions}
    """

common_instructions_for_query_generation = f'''
        1. Analyze the schema and limit the knowledge of the model to the schema. Identify the relevant tables and columns necessary to generate the query.
        2. Consider that multiple tables might need to be joined to get the correct answer.
        3. Add double quotes around all table names and column names in the query.
        4. If columns with the same name exist in multiple tables, specify which table the column belongs to by prefixing the column with the table name.
        5. Before generating the query check the schema again and see if the column name exists and the column is selected from the correct table itself.
        6. Do not give any details about the tables that are not mentioned in the Table and Columns Information.
    '''
