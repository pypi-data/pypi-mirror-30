# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 Fabian Wenzelmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class MedianVote(object):
    """Class for a vote in a median voting

    It contains the weight of a voter (default 1) and the value voted for by
    the voter. A vote should have a value >= 0.

    Attributes:
        value (int, float): Value the voter weighted for. value should be >= 0.
        weight (int): Weight of the voter (how many votes a single voter has).
    """

    def __init__(self, value, weight=1):
        self.value = value
        self.weight = weight

    def __repr__(self):
        return "median_voting.MedianVote(value=%d, weight=%d)" % (self.value, self.weight)


class MedianStatistics(object):
    """ A class for retrieving results from a median vote.

    The list of votes must be sorted for the functions to operate correctly.

    Args:
        votes (list of MedianVote): All votes you want results for.
        sorted (bool): Set to true if the list is already sorted according
            to weight in decreasing order. Otherwise the votes get sorted.

    Attributes:
        sorted_votes (list of MedianVote): The list of sorted votes.
    """

    def __init__(self, votes, is_sorted=False):
        if is_sorted:
            self.sorted_votes = votes
        else:
            self.sorted_votes = self.sort_votes(votes)

    @staticmethod
    def sort_votes(votes):
        """ Sorts the votes in decreasing order and returns the result.

        Usually you don't have to sort the elements by yourself, the __init__
        method will take care of this. But if the elements are already sorted
        from for example a database there is no need to sort them again.

        Args:
            votes (list of MedianVote): The votes to sort.

        Returns:
            list of MedianVote: The sorted votes.
        """
        return sorted(votes, key=lambda vote: vote.value, reverse=True)

    def details(self, values=None, is_sorted=False):
        """ Shows details about the vote.

        The result is a dictionary that contains an entry for each value from values. Each value is mapped to a tuple
        (num_weights, voters_list). num_weights is the number of vote weights that voted for >= value.
        voters_list is the list of all MedianVotes that voted for >= value (identified by an index
        in the sorted list).

        Note:
            This method is rather experimental at the moment.
            The votes in the result list are identified by the sorted id, that is it stores the position
            of that vote in the sorted list. Thus this index must not be the same as in the input list!
            One solution would be to use only sorted lists from the beginning or to subclass MedianVote and store
            additional information there.

        Args:
            values (list of integer): The entries of the result dictionary. That is the keys you want to receive results
                for. If it is not None then the set of all values appearing in the voting is used. It should not contain
                duplicates.
            is_sorted (bool): If set to True the values list / tuple is assumed to be sorted according to >. Otherwise
                values will be sorted first (without changing the input).

        Returns:
            dict int to tuple: See explanation above.
        """
        items = self.__prepare_values__(values, is_sorted)
        i, j = 0, 0
        _sum = 0
        all_voters = []
        res = dict()
        while i < len(self.sorted_votes) and j < len(items):
            next_entry = self.sorted_votes[i]
            next_compare = items[j]
            if next_entry.value >= next_compare:
                current_values = None
                if next_compare not in res:
                    current_values = list(all_voters)
                else:
                    current_values = res[next_compare][1]
                _sum += next_entry.weight
                all_voters.append(i)
                current_values.append(i)
                res[next_compare] = _sum, current_values
                i += 1
            else:
                if next_compare not in res:
                    res[next_compare] = _sum, list(all_voters)
                j += 1
        while j < len(items):
            next_compare = items[j]
            if next_compare not in res:
                res[next_compare] = _sum, list(all_voters)
            j += 1
        return res

    def __prepare_values__(self, values=None, is_sorted=False):
        if values is None:
            values = sorted({vote.value for vote in self.sorted_votes}, reverse=True)
        elif not is_sorted:
            values = sorted(values, reverse=True)
        return values

    def weight_sum(self):
        """ Returns the sum of all weights in the votes list.

        Returns:
            int: The sum of the weights.
        """
        return sum(vote.weight for vote in self.sorted_votes)

    def median(self, votes_required=None):
        """ Computes the median, i.e. the greatest value with a majority.

        You can either specify the number of notes required or let it be the
        half of the weight sum.

        Note:
            For a majority to be reached strictly more votes than
            votes_required are needed. For example: eight voters each with one
            vote, this means we must have more than 4 votes. For 15 votes we
            get that more than seven votes are required, i.e. at least 8.
            That is also the behaviour if you don't specify votes_required.

        Args:
            votes_required (int): The number of votes required for a majority. That is: > than (strictly!) this value
                are required. If it is not given it set to the weight sum // 2.
        """
        if votes_required is None:
            votes_required = self.weight_sum() // 2
        weight = 0
        for vote in self.sorted_votes:
            weight += vote.weight
            if weight > votes_required:
                return vote.value
        return None
