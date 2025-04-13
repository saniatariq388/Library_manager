import sqlite3
import streamlit as st


#database file name
DB_FILE = "library.db"

#-------------------- function database------------------------

# database connection establish karnay kay lay function
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # taakay hum row ke coumns ko dictionary ke tarha access kar sakay
    return conn

#-----------------initialize database----------------

#database ko initialize karo, table agar nahi hai to create karo
def initialize_db():
    conn = get_connection() 
    c = conn.cursor()  # cursor object banata hai jo SQL quries ko exc=ecute karnay kay liye use hota hai
    c.execute("""
         CREATE TABLE IF NOT EXISTS books(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              author TEXT NOT NULL,
              year INTEGER,
              genre TEXT,
              read INTEGER)
        """)
    conn.commit()  # database main changes ko save karta hai wo persist rahain
    conn.close()    # database connection ko close karta hai taki resources free ho jain


#-----------------function for adding book----------------
def add_book_db(title,author,year,genre,read):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
          INSERT INTO books(title,author,genre,year,read)
          VALUES (?,?,?,?,?)
        """, (title,author,genre,year,int(read))
    )
    conn.commit()
    conn.close()

#------------fuction for removing book------------


    # database se book remove karnay ke liay function  (book id ke basis par)
def remove_book_db(book_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM books WHERE id = ?',(book_id,))
        conn.commit()
        conn.close()

 #----------searching book-------

 # search qurey ke thrugh books dhoondhne ka function
def search_books_db(qurey):
     conn = get_connection()
     c = conn.cursor()
     c.execute(""""
               SELECT * FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? 
               """, (f'%{qurey.lower()}%',f'%{qurey.lower()}%'))
     results = c.fetchall()
     conn.close()
     return results



#-------------------------function for fetching------------------------------

# saree books fetch karnay kay liay

def fetch_all_books_db():
     conn = get_connection()
     c = conn.cursor()
     c.execute("SELECT * FROM books")
     results = c.fetchall()
     conn.close()
     return results


#----------------ststic libraray----------------

#library statistics ke liay function total books our itne read hue hai
def get_statistics_db():
     conn = get_connection()
     c = conn.cursor()
     c.execute('SELECT COUNT(*) FROM books')
     total_books = c.fetchone()[0]
     c.execute('SELECT COUNT(*) FROM books where READ = 1')
     read_books = c.fetchone()[0]
     conn.close()
     return total_books, read_books


#------------------- streamlit ---------------------
# streamlit par "ADD Book" ka ui

def add_book():
     st.subheader("📖 Add a New Book")
     with st.form("add_book_form"):
          title = st.text_input("Enter the book title:")
          author = st.text_input("Ente the author:")
          year = st.number_input("Enter the publication year:", min_value=0, step=1)
          genre =st.text_input("Enter the genre:")
          read_status = st.checkbox("Have you read this book?")
          submitted = st.form_submit_button("📌 Add Book")
          if submitted:
               if title and author and genre:
                    add_book_db(title,author,int(year),genre,read_status)
                    st.success(f"✅ '{title}' added successfully!")
               else:
                    st.error("⚠ Please fill in all fields before submitting.")


#streamlit par "Remove book " ka UI

def remove_book():
     st.subheader("🗑 Remove a Book")
     books = fetch_all_books_db()
     if books:
          # har book ko ek descriptiove label ke sath list karte hai
          options = {
               "Select a book": None
              }
          for book in books:
                label = f"{book['title']} by {book['author']} ({book['year']})"
                options[label] = book['id']

          selected = st.selectbox("Select a book to remove:", list(options.keys()))
          if selected != "Select a book "and st.button("❌ Remove Book"):
               book_id = options[selected]
               remove_book_db(book_id)
               st.success("🚮 Book removed successfully!")    

     else:  
        st.info("📭 Your library is empty. Add books first!")


#-------------------search book-----------

# streamlit par "search book" ka UI
 
def search_books():
     st.subheader("🔍 Search for a Book")
     search_query = st.text_input("Search by title or author:")
     if search_query:
          results = search_books_db(search_query)
          if results:
                st.write("### 📚 Search Results")
                for book in results:
                     st.write(f"{book['title']} by {book['author']} ({book['year']}) - {book['genre']} - {'✅ Read' if book['read'] else '❌  Unread'}")

                else:
                     st.warning("❌ No matching books found.")


#------------------------display books--------------
# display all books ka UI
def display_books():
    st.subheader("📚 Your Book Collection")                           
    books = fetch_all_books_db()
    if not books:
         st.info("📭 Your library is empty. Add some books!")
    else:
         for book in books:
              st.write(f"{book['title']} by {book['author']} ({book['year']}) - {book['genre']} - {'✅ Read' if book['read'] else '📖 Unread'}")     


# streamlit par " Display Statistics" ka UI

def display_statistics():
     st.subheader("📊 Library Statistics")
     total_books, read_books = get_statistics_db()
     unread_books = total_books - read_books
     read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
     st.metric("📚 Total Books", total_books)
     st.metric("✅ Books Read", read_books)
     st.metric("📖 Unread Books", unread_books)
     st.progress(read_percentage / 100)
     st.write(f"📈 Read Percentage: {read_percentage:.2f}%")

# main function jo streamlit UI ko manage karta hai
def main():
    st.title("📚 Personal Library Manager with Database")   
    initialize_db()
    # database our taable create karo agar exsist nahi karta


    menu = [
        "📖 Add a Book", 
        "🗑 Remove a Book", 
        "🔍 Search for a Book", 
        "📚 Display All Books", 
        "📊 Display Statistics", 
        "🚪 Exit"   
    ]
    choice = st.sidebar.radio("📌 Navigation", menu)

    if choice == "📖 Add a Book":
         add_book()
    elif choice == "🗑 Remove a Book":
         remove_book()
    elif choice == "🔍 Search for a Book":
         search_books()
    elif choice == "📚 Display All Books":
         display_books()
    elif choice == "📊 Display Statistics":
         display_statistics()
    elif choice == "🚪 Exit":
         st.success("📁 Library saved to database. Goodbye! 👋")
         st.stop()

if __name__ == "__main__":
     main()