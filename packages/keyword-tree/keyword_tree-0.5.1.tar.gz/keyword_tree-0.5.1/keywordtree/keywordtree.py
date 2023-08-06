#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
keywordtree

This class constructs a data structure that allows for optimal searching for keywords within a group of text.
It is designed to hold very large sets of keywords and quickly return a list of keywords it finds.  The purpose
is to have the most expensive cost (in time) occur once up front when the keyword tree is being built.

It has the ability to add and remove keywords on the fly, to export and import a built structure, and to limit the amount
of memory the tree can consume (requires package "Pympler").

Each keyword in the list can either be a simple string, or a dictionary with options:
    {
        'keyword': 'WORD',
        'case': False,  [optional, default False]
        'regex': True   [optional, default True]
    }

Requires: Python standard library "deepcopy", "json", and external library "pympler"
"""
from copy import deepcopy
import json
from pympler import asizeof
import re
import sys
# Defaults (feel free to adjust based upon your needs, wants, and/or desires)
DEFAULT_CASE = False
DEFAULT_REG = True

# Default Regular Expression Searching Syntax (probably shouldn't change this unless you know what you're doing...)
#REGEX = r'[^A-z]%s[^A-z]'
REGEX = r'\b%s\b'


class Tree:
    """
    A tree structure in which there exists one root, and keywords given
    become leaves and/or branches.  Each node is defined with:
        - Keyword
        - Is Branch
        - Is Leaf
        - Case Sensitive
        - List of subtrees

    List passed in should be a list of pairs:
        - Keyword           (text)
        - Case Sensitive    (bool) [optional, default: False]
    """
    def __init__(self, keywords=[], memory_limit=-1):
        self.keyword = None
        self.is_branch = False
        self.is_leaf = False
        self.case_sensitive = DEFAULT_CASE
        self.regex = DEFAULT_REG
        self.subtree = []
        self.parent = None
        self.MAX_MEM_SIZE = memory_limit  # In bytes, -1 = unlimited

        self.add_list(keywords)

    def add_list(self, keywords=[]):
        """
        Pass in a list of keywords to add.
        :param keywords:
        :return:
        """
        # have a list of adjusted keywords to take into account case sensitivity
        adjusted_keywords = []
        for word in keywords:
            w = word
            if isinstance(w, str):
                kw = w
                w = {}
                w['keyword'] = kw
                w['case'] = DEFAULT_CASE
                w['regex'] = DEFAULT_REG

            if isinstance(w, dict):
                if 'case' not in w:
                    w['case'] = DEFAULT_CASE
                if 'regex' not in w:
                    w['regex'] = DEFAULT_REG

            if not w['case']:
                w['keyword'] = w['keyword'].lower()

            adjusted_keywords.append(w)

        # for each keyword, find which subtree it belongs to...
        if len(keywords) == 0:
            return

        if len(adjusted_keywords) > 1:
            for word in adjusted_keywords:
                self.add_keyword(word)

        # if there is only one keyword, don't bother with any subtrees,
        # just assign that word as our keyword
        else:
            self.keyword = adjusted_keywords[0]['keyword']
            self.case_sensitive = adjusted_keywords[0]['case']
            self.regex = adjusted_keywords[0]['regex']

    def clone(self):
        """
        Perform a deep copy of the current object.
        """
        return deepcopy(self)

    def tree_size(self):
        return self.__size()

    def __size(self):
        """
        Checks the size of the entire tree.  If a limit has been set
        (defined by self.MAX_MEM_SIZE), return an object with the following:
            self['used'] = Size of Current Structure
            self['max']= Set max size we're allowed (-1 for unlimited; default)
        This only returns when we're at the root of the entire structure.
        :return:
        """
        # find the master root
        if self.parent is not None:
            return self.parent.__size()

        # get the total size of ourselves
        our_size = asizeof.asizeof(self)
        return {
            "used": our_size,
            "max": self.MAX_MEM_SIZE
        }

    def add_keyword(self, keyword):
        """
        Add a keyword to the current subtree.
        If the keyword fits any subtree of this structure, this function
        is called recursively for that subtree.

        If it doesn't, then other leaves of this subtree are examined.

        If a new branch can be derrived from this keyword and any particular
        leaf, a branch is created and that leaf (plus this keyword) is attached
        as leaves to that new branch, and the common leaf is removed from this
        subtree.

        If no leaf shares common beginnings with the keyword, then the keyword
        is simply added as a leaf to this subtree.

        The "keyword" being passed in is a pair of:
            - [0] = keyword         (text)
            - [1] = case sensitive  (bool)
        """
        # do nothing for empty keywords
        if keyword is None or keyword['keyword'] == '':
            return

        # run through each subtree to see if it matches any subtree
        for s in self.subtree:
            # if the root of the subtree is the first part of the keyword...
            if (keyword['keyword'].find(s.keyword) == 0) and s.is_branch:
                # then we add the keyword to this subtree
                s.add_keyword(keyword)
                return

        # if we got through and it never went into a subtree,
        # then see if we can create a new branch with another leaf...
        greatest_common_text = ''
        gc_index = 0
        gc_subtree = []
        index = 0  # used for removing leaves

        for s in self.subtree:
            # is this subtree a leaf?
            #if s.is_leaf:
            # find the most common letters between the two leaves...
            branch_letters = ''
            for i in range(len(keyword['keyword'])):
                if i < len(s.keyword) and keyword['keyword'][i] == s.keyword[i]:
                    branch_letters += keyword['keyword'][i]
                else:
                    break

            if len(greatest_common_text) < len(branch_letters):
                greatest_common_text = branch_letters
                gc_index = index
                gc_subtree = s.subtree

            index = index + 1

        # do nothing if it's a duplicate keyword
        if greatest_common_text == keyword['keyword']:
            # we have a duplicate!
            return

        # To prevent infinite recursion, if the only common
        # letters between our leaves is our current keyword, just add
        # all keywords as leaves
        if greatest_common_text != '' and greatest_common_text != self.keyword:
            # first create the branch
            branch = Tree([{'keyword': greatest_common_text, 'case': keyword['case'], 'regex': False}])
            branch.is_branch = True
            branch.parent = self

            # add the first leaf
            leaf1 = Tree([keyword])
            leaf1.is_leaf = True
            leaf1.parent = self
            branch.subtree.append(leaf1)

            # add the second leaf
            leaf2 = Tree([{'keyword': self.subtree[gc_index].keyword,
                                  'case': self.subtree[gc_index].case_sensitive,
                                  'regex': self.subtree[gc_index].regex}])
            leaf2.parent = self
            if gc_subtree == []:
                leaf2.is_leaf = True
            else:
                leaf2.is_leaf = False
                leaf2.regex = False

            leaf2.subtree = gc_subtree
            branch.subtree.append(leaf2)

            # make sure we don't exceed our size
            size_restrictions = self.__size()
            if size_restrictions['max'] > -1 and (size_restrictions['used'] +
                                                  asizeof.asizeof(branch) > size_restrictions['max']):
                raise MemoryError

            # add this branch!
            self.subtree.append(branch)

            # remove the old leaf
            self.subtree.pop(gc_index)

            # then we're done!
            return

        # if we have the same letters...
        if greatest_common_text != '' and greatest_common_text == self.keyword:
            # just add this as a leaf...
            leaf = Tree([keyword])
            leaf.is_leaf = True
            leaf.parent = self

            # make sure we don't exceed our size
            size_restrictions = self.__size()
            if size_restrictions['max'] > -1 and (size_restrictions['used'] +
                                                  asizeof.asizeof(leaf) > size_restrictions['max']):
                raise MemoryError

            self.subtree.append(leaf)
            return

        # if we didn't find any common letters between other leaves, or subtrees,
        # then we simply add this keyword as a new leaf
        leaf = Tree([keyword])
        leaf.is_leaf = True
        leaf.parent = self

        # make sure we don't exceed our size
        size_restrictions = self.__size()
        if size_restrictions['max'] > -1 and (size_restrictions['used'] +
                                              asizeof.asizeof(leaf) > size_restrictions['max']):
            raise MemoryError

        self.subtree.append(leaf)

    def remove_keyword(self, keyword):
        """
        Finds the leaf with a matching keyword and removes it.
        If the branch in which the leaf was removed from then only contains
        one leaf, the branch is removed and the lone leaf moves up one level.
        This action is recursive.
        :param keyword:
        :return:
        """
        w = keyword

        if isinstance(w, str) or type(w) is str:
            kw = w
            w = {}
            w['keyword'] = kw
            w['case'] = DEFAULT_CASE
            w['regex'] = DEFAULT_REG
            keyword = w

        # do nothing for empty keywords
        if keyword is None or w['keyword'] == '':
            return True

        # run through each subtree to see if it matches any subtree
        for s in self.subtree:
            # if the root of the subtree is the first part of the keyword...
            if (keyword['keyword'].find(s.keyword) == 0) and s.is_branch:
                # then we see if any of its leaves are our keyword...
                for leaf in s.subtree:
                    if leaf.is_leaf and leaf.keyword == keyword['keyword']:
                        # we found it!
                        s.subtree.remove(leaf)
                        s.__clean_branch()
                        return True
                    if leaf.is_branch:
                        return s.removeKeyword(keyword)

    def __clean_branch(self):
        """
        Private function that helps eliminate unnecessary branches
        after a leaf has been removed.  It climbs backwards from
        leaf-to-branch, converting branches of one leaf to leaves themselves.
        Theoretically this should only need to happen once, but recursion is
        built-in.
        :return:
        """
        if len(self.subtree) == 1:
            self.keyword = self.subtree[0].keyword
            self.is_branch = False
            self.is_leaf = True
            self.subtree = []
            self.parent.__clean_branch()
            return True
        return False

    def print_tree(self, details=False, level=0):
        """
        Prints the tree to std::out in an easy-to-read format
        to display the tree's structure.
        """
        for i in range(level):
            length = sys.stdout.write('\t')
        if level > 0:
            length = sys.stdout.write('- ')
        if self.keyword is None:
            length = sys.stdout.write("Tree Size: " + str(self.__size()['used']) + 'bytes\n')
            length = sys.stdout.write("root ")
            if details:
                if self.case_sensitive:
                    length = sys.stdout.write('Case Sensitive ')
                else:
                    length = sys.stdout.write('Not Case Sensitive ')

                if self.regex:
                    length = sys.stdout.write('Use Regular Expressions ')
                else:
                    length = sys.stdout.write("Doesn't Use Regular Expressions ")

                if self.is_branch:
                    length = sys.stdout.write('Branch ')
                else:
                    length = sys.stdout.write('Not Branch ')

                if self.is_leaf:
                    length = sys.stdout.write('Leaf ')
                else:
                    length = sys.stdout.write('Not Leaf ')

                    length = sys.stdout.write('Memory Allocation: ')
                    length = sys.stdout.write(self.MAX_MEM_SIZE)
                    length = sys.stdout.write('\n')

                if self.parent is not None:
                    length = sys.stdout.write('Has parent ')
                else:
                    length = sys.stdout.write('No parent assigned ')

                    length = sys.stdout.write('Subtree size: ')
                    length = sys.stdout.write(len(self.subtree))
                    length = sys.stdout.write('\n')
            else:
                length = sys.stdout.write('\n')

        else:
            if details:
                length = sys.stdout.write("'" + self.keyword + "'")
                if self.case_sensitive:
                    length = sys.stdout.write('Case Sensitive ')
                else:
                    length = sys.stdout.write('Not Case Sensitive ')

                if self.regex:
                    length = sys.stdout.write('Use Regular Expressions ')
                else:
                    length = sys.stdout.write("Doesn't Use Regular Expressions ")

                if self.is_branch:
                    length = sys.stdout.write('Branch ')
                else:
                    length = sys.stdout.write('Not Branch ')

                if self.is_leaf:
                    length = sys.stdout.write('Leaf ')
                else:
                    length = sys.stdout.write('Not Leaf ')

                length = sys.stdout.write('Memory Allocation: ')
                length = sys.stdout.write(self.MAX_MEM_SIZE)

                if self.parent is not None:
                    length = sys.stdout.write('Has parent ')
                else:
                    length = sys.stdout.write('No parent assigned ')

                length = sys.stdout.write('Subtree size: ')
                length = sys.stdout.write(len(self.subtree))
            else:
                length = sys.stdout.write("'" + self.keyword + "'")

        for s in self.subtree:
            s.print_tree(details, level + 1)

    def prune(self, incoming_text):
        """
        Prune("Text to search")

        Each subtree/leaf is examined and compared to the passed in text.
        Any branch whose text is not found in the passed in text is removed.
        The resulting tree will only hold leaves that are found in the text passed in.
        A list of these leaves is returned, while the tree structure is modified.

        Recursive Note:
            If the current subtree's text isn't found, it returns an empty list.
            This should indicate that this subtree should be removed!!
        """
        # first, if we're the root, then make two copies of the text...
        if self.keyword is None:
            text = [incoming_text, incoming_text.lower()]
        else:
            text = incoming_text

        # first check if our current keyword is in the passed in text (if we're not root)
        if self.keyword is not None and self.is_branch:
            if self.case_sensitive:
                try:
                    if text[0].find(self.keyword) == -1:
                        return []
                except:
                    return []
            else:
                if text[1].find(self.keyword) == -1:
                    return []
                try:
                    if text[1].find(self.keyword) == -1:
                        return []
                except:
                    return []

        # if we're a leaf, we need to check if we should use regular expressions
        if self.keyword is not None and self.is_leaf:
            if self.case_sensitive:
                if self.regex:
                    match = re.search(REGEX % (self.keyword), text[0])
                    if match is None:
                        return []
                else:
                    try:
                        if text[0].find(self.keyword) == -1:
                            return []
                    except:
                        return []
            else:
                if self.regex:
                    match = re.search(REGEX % (self.keyword), text[1])
                    if match is None:
                        return []
                else:
                    try:
                        if text[1].find(self.keyword) == -1:
                            return []
                    except:
                        return []

        # list we'll return back
        leaf_list = []

        # are we a leaf?
        if self.is_leaf and not self.is_branch:
            leaf_list.append(self.keyword)

        # now run through each subtree, removing if it returns an empty list
        to_remove = [] # used for deleting subtrees
        for tree in self.subtree:
            subtree_list = tree.prune(text)
            if subtree_list == []:
                # remove this subtree
                to_remove.append(tree)
            else:
                leaf_list += (subtree_list)

        # remove our list of subtrees to remove
        for r in to_remove:
            self.subtree.remove(r)

        # return our list of found leaves!
        return leaf_list

    def dump(self):
        """
        Returns a JSON String object representing the tree.

        Used for storing the tree structure externally.
        Usage: file.write(tree.dump())
        :return:
        """
        return json.dumps(self.__dump_tree())

    def __dump_tree(self):
        """
        Private recursive function that generates the JSON object
        constructed for dumping.
        :return:
        """
        root = {}
        root['keyword'] = self.keyword
        root['is_branch'] = self.is_branch
        root['is_leaf'] = self.is_leaf
        root['case_sensitive'] = self.case_sensitive
        root['regex'] = self.regex
        root['memory_limit'] = self.MAX_MEM_SIZE
        root['subtree'] = []
        for tree in self.subtree:
            root['subtree'].append(tree.__dump_tree())

        return root

    def load(self, json_tree):
        """
        Given the self is an empty KeyTree object, pass in a JSON string of
        a dumped tree, the tree will self-construct based on the JSON string
        passed in.  Meant to be used with the "self.dump" function.

        Usage:
            file = open('saved_tree.json', 'r')
            tree = KeywordTree()
            tree.load(file.read())
        :param json_tree: JSON String of a tree - based on the dump from self.dump()
        :return:
        """
        dumped_tree = json.loads(json_tree)
        return self.__load_tree(dumped_tree)

    def __load_tree(self, trunk):
        """
        Private recursive function that constructs the
        tree based on the passed in JSON object.
        :param trunk: JSON object of the current subtree
        :return:
        """
        self.keyword = trunk['keyword']
        self.is_branch = trunk['is_branch']
        self.is_leaf = trunk['is_leaf']
        self.case_sensitive = trunk['case_sensitive']
        self.regex = trunk['regex']
        self.MAX_MEM_SIZE = trunk['memory_limit']
        self.subtree = []

        for subtree in trunk['subtree']:
            new_tree = Tree()
            new_tree.__load_tree(subtree)
            new_tree.parent = self
            self.subtree.append(new_tree)

        return True
