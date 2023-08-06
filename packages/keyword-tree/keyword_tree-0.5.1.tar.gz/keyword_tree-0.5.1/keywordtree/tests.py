from keywordtree import Tree

import unittest


def tree_too_big():
    Tree(
        keywords=['bobby', 'blanket', 'bubbles', 'book', 'blood', 'bar', 'cat', 'category', 'car', 'cost'],
        memory_limit=1
    )


class KeywordTreeTest(unittest.TestCase):
    """Tests for `primes.py`."""

    def test_construction(self):
        """Can we construct a tree and have the result be of Tree type?"""
        tree = Tree(
            keywords=['bobby', 'blanket', 'bubbles', 'book', 'blood', 'bar', 'cat', 'category', 'car', 'cost'])
        self.assertTrue(tree.__class__ == Tree)

    def test_maximum_memory_allocation(self):
        """If we set the memory limit too small, do we get an error?"""
        self.assertRaises(MemoryError, tree_too_big)

    def test_memory_limit_pass(self):
        """If we set the memory limit large enough, do we get back a Tree object?"""
        tree = Tree(
            keywords=['bobby', 'blanket', 'bubbles', 'book', 'blood', 'bar', 'cat', 'category', 'car', 'cost'],
            memory_limit=1024 * 1024
        )
        self.assertTrue(tree.__class__ == Tree)

    def test_construction_with_dictionary(self):
        """If we construct a dictionary first, can we still construct a tree?"""
        keyword_list = [
            {'keyword': 'Notre Dame', 'case': True},
            {'keyword': 'university', 'regex': False},
            {'keyword': 'Fighting', 'case': True, 'regex': False},
            'irish'
        ]
        tree = Tree(keywords=keyword_list)
        self.assertTrue(tree.__class__ == Tree)

    def test_adding_dictionary_to_existing_tree(self):
        """If we create an empty tree, can we add a dictionary list to it later?"""
        tree = Tree()
        size_a = tree.tree_size()
        keyword_list = [
            {'keyword': 'Notre Dame', 'case': True},
            {'keyword': 'university', 'regex': False},
            {'keyword': 'Fighting', 'case': True, 'regex': False},
            'irish'
        ]
        tree.add_list(keyword_list)
        size_b = tree.tree_size()
        another_keyword_list = [
            {'keyword': 'football', 'case': True}
        ]
        tree.add_list(another_keyword_list)
        size_c = tree.tree_size()
        self.assertGreater(size_b['used'], size_a['used'])
        self.assertGreater(size_c['used'], size_b['used'])

    def test_removing_word(self):
        """Can we remove a word?"""
        # tree with a list of keywords passed in
        tree = Tree(
            keywords=['bobby', 'blanket', 'bubbles', 'book', 'blood', 'bar', 'cat', 'category', 'car', 'cost'])
        # then remove the word 'bubbles'
        dump = tree.dump()
        self.assertTrue('bubbles' in str(dump))
        tree.remove_keyword('bubbles')
        dump = tree.dump()
        self.assertFalse('bubbles' in str(dump))

    def test_exporting_and_importing(self):
        """If we construct a tree, can we take the export of it and load it into a second tree, and have the results
        be the same?
        """
        tree1 = Tree(
            keywords=['bobby', 'blanket', 'bubbles'])
        dump = tree1.dump()
        self.assertTrue('bobby' in str(dump))
        self.assertTrue('blanket' in str(dump))
        self.assertTrue('bubbles' in str(dump))

        # load
        tree2 = Tree()
        tree2.load(dump)
        dump = tree2.dump()
        self.assertTrue('bobby' in str(dump))
        self.assertTrue('blanket' in str(dump))
        self.assertTrue('bubbles' in str(dump))



if __name__ == '__main__':
    unittest.main()
