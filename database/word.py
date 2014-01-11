import sqlite3

from . import connection, dict_factory

class Word:
    @classmethod
    def from_story_id(cla, story_id):
        """
        Get the first word for a story
        """
        c = connection.cursor()
        c.execute("SELECT wordID, storyID, word, author, parentID FROM words WHERE storyID = ? and parentID IS NULL", (story_id,))
        result = c.fetchone()
        if result:
            return cla(result[0],result[1], result[2], result[3], result[4])
    
    @classmethod
    def from_id(cla, word_id):
        c = connection.cursor()
        c.execute("SELECT wordID, storyID, word, author, parentID FROM words WHERE wordID = ?", (word_id,))
        result = c.fetchone()
        if result:
            return cla(result[0],result[1], result[2], result[3], result[4])
        
    def __init__(self, id, story_id, value, author, parent_id = None):
        self.id = id
        self.parent_id = parent_id
        self.story_id = story_id
        self.value = value
        self.author = author
        if not id:
            self.save()

    def __str__(self):
        return self.value
        
    def add_child(self, value, author):
        new_word = Word(False, self.story_id, value, author, self.id)
        new_word.save()
        return new_word
    def remove(self):
        for child in self.children:
            child.remove()
        c = connection.cursor()
        c.execute("""
        DELETE FROM words WHERE wordID = ?
        """, (self.id,))
        connection.commit()
        
    @property
    def word_count(self):
        count = 1 #account for self
        for child in self.children:
            count += child.word_count
        return count
    
    @property
    def children(self):
        c = connection.cursor()
        
        c.execute("""
            SELECT wordID, storyID, word, author, parentID FROM
                words
            WHERE
                parentID = """ + str(self.id) + """
        """)
        
        children = []
        for childWord in c:
            #id, parentID, storyID, word
            children.append(Word(childWord[0], childWord[1], childWord[2], childWord[3], childWord[4]))
        
        return children
    
    def save(self):
        c = connection.cursor()
        if self.id:
            #print('[save] update')
            c.execute("""
                UPDATE words
                SET
                storyID = ?
                ,word = ?
                ,parentID = ?
                ,author = ?
                WHERE
                    wordID = ?
                """, (self.story_id, self.value, self.parent_id, self.author, self.id))
            connection.commit()
        else:
            #print('[save] insert')
            c.execute("""
                INSERT INTO words VALUES (NULL,?,?,?,?)
                """, (self.parent_id, self.story_id, self.value, self.author))
            connection.commit()
            self.id = c.lastrowid
