import streamlit as st
from tinydb import TinyDB, Query

# Initialize the databases
db_users = TinyDB('database_users.json')
db_posts = TinyDB('database_posts.json')

# Function to create or get user info from the database
def get_user(username):
    User = Query()
    user_info = db_users.table('users').get(User.username == username)
    return user_info

# Function to check if the username exists
def username_exists(username):
    User = Query()
    return db_users.table('users').contains(User.username == username)

# Function to register a new user
def register_user(username, password):
    if not username_exists(username):
        db_users.table('users').insert({'username': username, 'password': password, 'profile_pic': None, 'description': None})
        return True
    else:
        return False

# Function to authenticate the user
def authenticate_user(username, password):
    User = Query()
    user_info = db_users.table('users').get((User.username == username) & (User.password == password))
    return user_info

# Function to update user profile
def update_profile(username, profile_pic, description):
    User = Query()
    db_users.table('users').update({'profile_pic': profile_pic, 'description': description}, User.username == username)

# Function to add a new post
def add_post(username, image_url, title, description):
    db_posts.table('posts').insert({'username': username, 'image_url': image_url, 'title': title, 'description': description, 'likes': 0, 'dislikes': 0, 'comments': []})

# Function to get all posts for the feed
def get_all_posts():
    return db_posts.table('posts').all()

# Function to react to a comment (like or dislike)
def react_to_comment(post_id, comment_id, reaction_type):
    posts = db_posts.table('posts')
    post = posts.get(doc_id=post_id)

    if post:
        comments = post['comments']
        if 0 <= comment_id < len(comments):
            comment = comments[comment_id]
            if reaction_type == 'likes':
                comment['likes'] += 1
            elif reaction_type == 'dislikes':
                comment['dislikes'] += 1

            posts.update({'comments': comments}, doc_ids=[post_id])

# Function to react to a post (like or dislike)
def react_to_post(post_id, reaction_type):
    posts = db_posts.table('posts')
    post = posts.get(doc_id=post_id)

    if post:
        if reaction_type == 'likes':
            post['likes'] += 1
        elif reaction_type == 'dislikes':
            post['dislikes'] += 1

        posts.update(post, doc_ids=[post_id])

# Streamlit App
def main():
    st.title('FussionLink')

    # Toggle for dark and light modes
    dark_mode = st.checkbox('Dark Mode', key='dark_mode')

    # Apply dark mode if selected
    if dark_mode:
        st.markdown(
            """
            <style>
                body {
                    color: white;
                    background-color: #222;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Logout Button in the sidebar
    if st.sidebar.button('Logout'):
        st.session_state.pop('user')
        st.experimental_rerun()

    page = st.sidebar.radio('Select a page', ['Login', 'Register', 'Feed', 'Profile', 'Add Post'])

    if page == 'Login':
        st.subheader('Login')
        username = st.text_input('Username', value='')
        password = st.text_input('Password', type='password', value='')
        if st.button('Login'):
            user_info = authenticate_user(username, password)
            if user_info:
                st.success(f'Welcome, {username}! You are logged in.')
                st.session_state.user = user_info
                st.experimental_rerun()
                # Clear input values
                st.session_state.sync()
            else:
                st.error('Invalid username or password')

    elif page == 'Register':
        st.subheader('Register')
        new_username = st.text_input('Username', value='')
        new_password = st.text_input('Password', type='password', value='')
        if st.button('Register'):
            if register_user(new_username, new_password):
                st.success(f'Account created for {new_username}! You can now log in.')
                st.session_state.user = get_user(new_username)
                st.experimental_rerun()
                # Clear input values
                st.session_state.sync()
            else:
                st.error('Username already exists. Please choose another username.')

    elif page == 'Feed':
        st.subheader('Feed')
        if 'user' in st.session_state:
            posts = get_all_posts()
            for post in posts:
                st.image(post['image_url'], caption=post['title'])
                st.write(f"Posted by: {post['username']}")
                st.write(f"Likes: {post['likes']}")
                st.write(f"Dislikes: {post['dislikes']}")
                st.write(f"Description: {post['description']}")
                st.write("Comments:")
                for comment_id, comment in enumerate(post['comments']):
                    st.write(f"Comment {comment_id + 1}: {comment}")
                    like_button_key = f"like_comment_{post.doc_id}_{comment_id}"
                    dislike_button_key = f"dislike_comment_{post.doc_id}_{comment_id}"
                    if st.button(f"Like Comment {comment_id + 1}", key=like_button_key):
                        react_to_comment(post.doc_id, comment_id, 'likes')
                    if st.button(f"Dislike Comment {comment_id + 1}", key=dislike_button_key):
                        react_to_comment(post.doc_id, comment_id, 'dislikes')
                    st.text_area(f"Add a Comment for Post {post.doc_id}", key=f"comment_input_{post.doc_id}")
                    comment_button_key = f"add_comment_{post.doc_id}"
                    if st.button(f"Submit Comment for Post {post.doc_id}", key=comment_button_key):
                        new_comment = st.session_state[f"comment_input_{post.doc_id}"]
                    if new_comment:
                        post['comments'].append(new_comment)
                        db_posts.update({'comments': post['comments']}, doc_ids=[post.doc_id])

                like_button_key = f"like_post_{post.doc_id}"
                dislike_button_key = f"dislike_post_{post.doc_id}"
                if st.button(f"Like Post {post.doc_id}", key=like_button_key):
                    react_to_post(post.doc_id, 'likes')
                if st.button(f"Dislike Post {post.doc_id}", key=dislike_button_key):
                    react_to_post(post.doc_id, 'dislikes')

                if 'user' in st.session_state and st.session_state.user['username'] == post['username']:
                    edit_button_key = f"edit_post_{post.doc_id}"
                    if st.button(f"Edit Post {post.doc_id}", key=edit_button_key):
                        # Add functionality for editing post
                        new_title = st.text_input('Edit Title', value=post['title'])
                        new_description = st.text_input('Edit Description', value=post['description'])
                        if st.button('Save Edit'):
                            # Implement function to update post
                            post['title'] = new_title
                            post['description'] = new_description
                            db_posts.update(post, doc_ids=[post.doc_id])
                            st.success("Post updated successfully!")

    elif page == 'Add Post':
        st.subheader('Add New Post')
        new_image_url = st.text_input("Image URL", key="new_image_url")
        new_title = st.text_input('Title', key="new_title")
        new_description = st.text_input('Description', key="new_description")
        if st.button('Post', key='post_button'):
            if 'user' in st.session_state:
                add_post(st.session_state.user['username'], new_image_url, new_title, new_description)
                st.success("Post added successfully!")
            else:
                st.warning('Please log in to post.')

    elif page == 'Profile':
        st.subheader('Profile')
        if 'user' in st.session_state:
            user_info = st.session_state.user
            st.write(f"Username: {user_info['username']}")
            st.write(f"Description: {user_info['description']}")

            # Check if profile_pic is not None before displaying
            if user_info['profile_pic']:
                st.image(user_info['profile_pic'], caption='Profile Picture')
            else:
                st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Grosser_Panda.JPG/1280px-Grosser_Panda.JPG", caption='Default Profile Picture')

            st.subheader("Edit Profile:")
            new_profile_pic = st.text_input("New Profile Picture URL", key="new_profile_pic")
            new_description = st.text_input('New Description', value=user_info['description'], key="new_description_profile")
            if st.button('Update Profile', key='update_profile_button'):
                update_profile(user_info['username'], new_profile_pic, new_description)
                st.success("Profile updated successfully!")

    else:
        st.error('Please login or register.')

if __name__ == '__main__':
    main()