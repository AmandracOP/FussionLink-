import streamlit as st
from tinydb import TinyDB, Query

# Initialize TinyDB for storing user profiles and posts
db_users = TinyDB('users.json')
db_posts = TinyDB('posts.json')

# Sign-up Page
def signup_page():
    st.title('Sign Up')

    # Simulating Google signup by entering a username
    username = st.text_input('Enter Username')

    if st.button('Sign Up'):
        # Simulate signup by adding a user to the database
        user = {'username': username}
        db_users.insert(user)
        st.success('Signed up successfully!')

# Add Post Page
def add_post_page():
    st.title('Add a Post')

    # Simulated user selection after signup
    users = db_users.all()
    user = st.selectbox('Select User', [u['username'] for u in users])

    title = st.text_input('Title')
    content = st.text_area('Content')
    image_url = st.text_input('Image URL')

    if st.button('Submit'):
        # Simulate saving the post to the database
        post = {
            'user': user,
            'title': title,
            'content': content,
            'image_url': image_url  # Store the URL of the image
        }
        db_posts.insert(post)
        st.success('Post added successfully!')

# Feed Display Page
def feed_display_page():
    st.title('Post Feed')

    # Center the posts
    st.markdown('<style> .center { display: flex; justify-content: center; align-items: center; } </style>', unsafe_allow_html=True)
    st.markdown('<div class="center">', unsafe_allow_html=True)

    # Display posts from the database
    posts = db_posts.all()
    for post in posts:
        with st.container():
            st.image(post['image_url'], width=200)  # Display the image using the stored URL
            st.write(f"**Title:** {post['title']}")
            st.write(f"**By:** {post['user']}")
            st.write(f"**Content:** {post['content']}")

    st.markdown('</div>', unsafe_allow_html=True)




# Main Streamlit App
def main():
    page = st.sidebar.selectbox("Select Page", ["Signup", "Add Post", "Feed Display"])

    if page == "Signup":
        signup_page()
    elif page == "Add Post":
        add_post_page()
    elif page == "Feed Display":
        feed_display_page()

if __name__ == "__main__":
    main()
