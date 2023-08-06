#!/usr/bin/env python3

# Copyright (C) 2016 Institute of Computer Science of the Foundation for Research and Technology - Hellas (FORTH)
# Authors: Michalis Bamiedakis, Dimitris Mavrommatis and George Nomikos
#
# Contact Author: George Nomikos
# Contact Email: gnomikos [at] ics.forth.gr
#
# This file is part of traIXroute.
#
# traIXroute is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# traIXroute is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with traIXroute.  If not, see <http://www.gnu.org/licenses/>.

from traixroute.controller import traixroute_output, string_handler
from traixroute.detector.remote_peering import remote_peering
from math import fabs
import os
import sys
import itertools


class detection_rules():
    '''
    This class is responsible for handling and applying the rules in a given traceroute path
    to infer IXP crossing links.
    '''

    def __init__(self):

        # rules: A list of the condition parts of the rules.
        self.rules = []
        # asmt: A list of the assessment parts of the rules.
        self.asmt = []
        # remote_peering: An instance of the remote peering class.
        self.remote_peering = remote_peering()

    def rules_extract(self, mypath):
        '''
        Opens the rules.txt file and loads the IXP detection rules.
        Input: 
            a) file: The file that contains the rules.
        '''
        
        file = '/configuration/rules.txt'
        try:
            with open(mypath + '/configuration/rules.txt', 'r') as f:
                rules = [line.strip() for line in f.readlines()]
        except:
            print(file + ' does not exist. Exiting.')
            sys.exit(0)
        [delimiters, expressions] = self.load_syntax_rules(
            'configuration/expressions.txt', 'configuration/delimeters.txt', mypath)
        
        general_flag = True   
        for i,item in enumerate(rules):
            temp = item.split('#')
            temp[0] = temp[0].replace(' ', '')
            if temp[0] != '':
                flag = True
                temp = (temp[0].split(':'))
                if len(temp) != 2:
                    flag = False
                    general_flag = False
                    print('-->Error with rule in line ' + (str(i + 1)) +
                          'not included. Expected one condition and one assessment part respectively.')
                    
                array = temp[0].split('-')
                for node in array:
                    if len(array) > 3:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected a maximum rule length of 3.')
                    elif len(array) < 2:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected a minimum rule length of 2.')
                    elif '(' in node and ')' not in node:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected \')\' at the end of ' + node + '.')
                    elif '(' in node and 'and' not in node:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected 1 \'and\' at the middle of ' + node + '.')
                    elif ')' in node and '(' not in node:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected one \'(\' at the beginning of ' + node + '.')
                    elif node.count('(') > 1:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected only 1 \'(\' at the beginning of ' + node + '.')
                    elif node.count(')') > 1:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected only 1 \')\' at the end of ' + node + '.')
                        
                    node = node.replace('(', '')
                    node = node.replace(')', '')
                    if not self.check_syntax_rules(node, expressions, delimiters):
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Wrong syntax in ' + node + '.')
                if 'IXP_IP' not in temp[0]:
                    flag = False
                    general_flag = False
                    print('-->Error with rule in line ' + (str(i + 1)) +
                          ' not included. Expected an IXP_IP in ' + temp[0] + '.')
                elif flag:
                    node = temp[1].replace(' ', '')
                    if 'a' != node and 'b' != node and 'aorb' != node and 'aandb' != node and '?' != node:
                        flag = False
                        general_flag = False
                        print('-->Error with rule in line ' + (str(i + 1)) +
                              ' not included. Expected a valid assessment (e.g., a, b, a or b, a and b).')
                
                if flag:
                    self.rules.append(array)
                    self.remote_peering.check_rule(array, len(self.rules) - 1)
                    self.asmt.append(temp[1])
                    
        if general_flag:
            output = traixroute_output.traixroute_output()
            output.print_rules_number(self.rules, mypath+file)
        else:
            sys.exit(0)

    def resolve_path(self, path, output, path_info_extract, db_extract, traIXparser):
        '''
        Applies the IXP detection rules upon the resolved path printing all the potential IXP crossing links.
        Input:
            a) path: The IP path.
            b) mypath: The path to the traIXroute folder.
            c) output: The traixroute_output class.
            d) path_info_extract: The path_info_extract class.
            e) db_extract: The database_extract class.
            f) traIXparser: The traIXparser class.           
        '''
        
        num = 1
        rule_hits = [0] * len(self.rules)
        asn_print = traIXparser.flags['asn']
        print_rule = traIXparser.flags['rule']
        # asn2names : Contains the total IXP membership info for each ASN.
        # asn2names: {'ASN': [IXP long name, IXP short name ]}
        asn2names = db_extract.asnmemb
        cc_tree = db_extract.cc_tree
        self.remote_peering.rp_database = db_extract.remote_peering
        
        # Info related to the candidate traceroute path.
        path_asn = path_info_extract.asn_list
        temp_path_asn = [''] * len(path_asn)
        encounter_type = path_info_extract.type_vector
        ixp_ip_indices = path_info_extract.ixp_ip_indices
        ixp_long = path_info_extract.ixp_long_names
        ixp_short = path_info_extract.ixp_short_names
        
        for i in ixp_ip_indices:
            asn_list1 = path_asn[i - 1].split('_')
            asn_list3 = path_asn[i].split('_')
            if len(path) > i + 1:
                asn_list2 = path_asn[i + 1].split('_')
            else:
                asn_list2 = '*'
                
            for asn1 in asn_list1:
                # In case of MOAS, all the possible AS paths are checked for
                # IXP crossing.
                for asn2 in asn_list2:
                    for asn3 in asn_list3:
                        temp_path_asn[i - 1] = asn1
                        temp_path_asn[i] = asn3
                        if len(path_asn) > i + 1:
                            temp_path_asn[i + 1] = asn2
                        
                        for j,item_rule in enumerate(self.rules):
                            cur_rule = item_rule
                            cur_asmt = self.asmt[j]
#                            print('cur_rule',cur_rule)

                            # Check if the condition part of a candidate rule
                            # is satisfied in order to proceed with the
                            # assessment part.
                            current_hop = 1
                            if i < len(path) - 1:
                                cur_path_asn = temp_path_asn[i - 1:i + 2]
                                temp_ixp_long = ixp_long[i - 1:i + 2]
                                temp_ixp_short = ixp_short[i - 1:i + 2]
                                cur_encounter_type = encounter_type[i - 1:i + 2]
                                cur_path = path[i - 1:i + 2]
                            else:
                                cur_path_asn = temp_path_asn[i - 1:i + 1]
                                temp_ixp_long = ixp_long[i - 1:i + 1]
                                temp_ixp_short = ixp_short[i - 1:i + 1]
                                cur_encounter_type = encounter_type[i - 1:i + 1]
                                cur_path = path[i - 1:i + 1]
#                            print('cur_path',cur_path)
#                            print('cur_path_asn',cur_path_asn)
                            
                            set_ixp_short = list(itertools.product(*temp_ixp_short))
                            set_ixp_long = list(itertools.product(*temp_ixp_long))
                            
                            for ixp in range(0, len(set_ixp_short)):
                                cur_ixp_long = list(set_ixp_long[ixp])
                                cur_ixp_short = list(set_ixp_short[ixp])
                                rule_check = self.check_rules(
                                    cur_path, cur_rule, cur_path_asn, current_hop, cur_ixp_long, cur_ixp_short, asn2names, cur_encounter_type)
                                if rule_check:
                                    if cur_asmt != '?':
                                        rule_hits[j] += 1
                                    if self.remote_peering.rule_hit(j):
                                        self.remote_peering.temp_index = j
                                        output.print_result(asn_print, print_rule, cur_ixp_long, cur_ixp_short, cur_path_asn,path, i, j, num, ixp_short, cur_asmt, ixp_long, cc_tree, self.remote_peering)
                                    else:
                                        output.print_result(asn_print, print_rule, cur_ixp_long, cur_ixp_short,cur_path_asn, path, i, j, num, ixp_short, cur_asmt, ixp_long, cc_tree)
                                    num += 1
        return rule_hits

    def check_rules(self, path, rule, path_asn, path_cur, ixp_long, ixp_short, asn2names, encounter_type):
        '''                      
        Checks if the condition part of a rule is satisfied.
        Input:
            a) rule: The condition part of the candidate IXP detection rule.
            b) path_asn: The AS path.
            c) path_cur: The current hop in the path.
            d) ixp_long, ixp_short: The long and short IXP names.
            e) asn2names: A dictionary with a list of lists of short and long IXP names in which an AS is member - {ASN}=[[name long,name short],[name long,name short]...].
            f) encounter_type: The resolved IP path based on the encountered types (IXP IP, IXP Prefix, Normal IP, Illegal IP).
            g) path: The IP path.
        Output:
            True if the expression is satisfied, False otherwise.
        '''

        if len(rule) > len(path_asn):
            return False
        for i,item in enumerate(rule):
            if len(path_asn) > path_cur + i - 1:
                if ('IXP_IP' in item and '!AS_M' in item) and 'IXP prefix' not in encounter_type[path_cur + i - 1] and 'IXP IP' not in encounter_type[path_cur + i - 1]:
                    return False
                elif 'IXP_IP' in item and 'AS_M' in item and '!' not in item and 'IXP IP' not in encounter_type[path_cur + i - 1]:
                    return False
                elif ('IXP_IP' not in item or '!AS_M' not in item) and 'IXP prefix' in encounter_type[path_cur + i - 1]:
                    return False
                elif ('IXP_IP' not in item or 'AS_M' not in item) and 'IXP IP' in encounter_type[path_cur + i - 1]:
                    return False

        # Applies each condition of the condition part of the candidate rule onto the path.
        string_h = string_handler.string_handler()
        check = 0
        for i,expression in enumerate(rule):
        
            # The current condition of the condition part of the rule.
            current = path_cur + i - 1

            # Checking for IXP membership based on a non-IXP IP.
            if '!AS_M' in expression and 'and' not in expression and path_cur != current:
               # Finds the path_asn in the routeview path_asn dict. If not, an
               # assessment is not possible.
                check += 1
                if path_asn[current] == '*' and encounter_type[current] != 'IXP prefix':
                    return False

                if encounter_type[path_cur] == 'IXP IP' or encounter_type[path_cur] == 'IXP prefix':
                    as_names = ''
                    if path_asn[current] in asn2names.keys():
                        as_names = asn2names[path_asn[current]]
                        ix_long = ixp_long[path_cur]
                        ix_short = ixp_short[path_cur]
                else:
                    as_names = ''
                    if path_asn[path_cur] in asn2names.keys():
                        as_names = asn2names[path_asn[path_cur]]
                        ix_long = ixp_long[current]
                        ix_short = ixp_short[current]
                for node in as_names:
                    for name in node:
                        if (string_h.string_comparison(ix_long, name) or string_h.string_comparison(ix_short, name)):
                            return False
                if not self.check_number(rule, expression, path_asn, current, i, encounter_type, '!AS_M'):
                    return False

            elif 'AS_M' in expression and 'and' not in expression and path_cur != current:
                if path_asn[current] == '*' and encounter_type[current] != 'IXP prefix':
                    return False
                check += 1
                flag = False

                if encounter_type[path_cur] == 'IXP IP' or encounter_type[path_cur] == 'IXP prefix':
                    as_names = ''
                    if path_asn[current] in asn2names.keys():
                        as_names = asn2names[path_asn[current]]
                    ix_long = ixp_long[path_cur]
                    ix_short = ixp_short[path_cur]
                else:
                    as_names = ''
                    if path_asn[path_cur] in asn2names.keys():
                        as_names = asn2names[path_asn[path_cur]]
                    ix_long = ixp_long[current]
                    ix_short = ixp_short[current]
                for node in (as_names):
                    for name in node:
                        if string_h.string_comparison(ix_long, name) or string_h.string_comparison(ix_short, name):
                            flag = 1
                            break
                if not flag:
                    return False
                if not self.check_number(rule, expression, path_asn, current, i, encounter_type, 'AS_M'):
                    return False

            if '*' in expression and path[current] != '*':
                return False
            # Checking for IXP IP or Prefix based on either IXP membership or
            # Prefixes data.
            if 'IXP_IP' in expression and '!AS_M' in expression:
                check += 1
                if not self.check_names(rule, expression, current, i, encounter_type, 'IXP_IP', ixp_long, ixp_short):
                    return False
                elif not self.check_number(rule, expression, path_asn, current, i, encounter_type, '!AS_M'):
                    return False
            elif 'IXP_IP' in expression and 'AS_M' in expression:
                check += 1
                if not self.check_names(rule, expression, current, i, encounter_type, 'IXP_IP', ixp_long, ixp_short):
                    return False
                elif not self.check_number(rule, expression, path_asn, current, i, encounter_type, 'AS_M'):
                    return False

        if len(rule) > 2 and len(path_asn) > current + 1:
            check += 1
            if not self.check_edges(rule, path_asn, current, 'AS_M', ixp_long, ixp_short):
                return False
            elif not self.check_edges(rule, path_asn, current, 'IXP_IP', ixp_long, ixp_short):
                return False
        if check:
            return True
        else:
            return False

    def check_edges(self, rule, path_asn, current, str_to_chk, ixp_long, ixp_short):
        '''
        Checks the similarity of the concatenated numbers in case of AS_M and IXP_IP keywords of the border hops of a rule with hop window of size three.
        Input:
            a) rule: The current rule.
            b) path_asn: The AS path.
            c) current: The current hop in the path.
            d) str_to_chk: The condition keyword of the rule.
            e) ixp_long,ixp_short: The long and short IXP names.
        Output: 
            True if the condition is satisfied, False otherwise.
        '''
        
        [final1, final2] = self.find_numbers(rule, str_to_chk, current, False)

        if final1 == '' or final2 == '':
            return True
        if self.is_int(final1) and self.is_int(final2) and 'AS_M' in str_chk:
            if (final1 == final2 and path_asn[current - 1] != path_asn[current + 1]) or (final1 != final2 and path_asn[current - 1] == path_asn[current + 1]):
                return False
        elif self.is_int(final1) and self.is_int(final2) and 'IXP_IP' in str_chk:
            string_hanlde = string_handler.string_handler()
            flag = (string_handle.string_comparison(ixp_long[current - 1], ixp_long[
                    current + 1]) or string_handle.string_comparison(ixp_short[current - 1], ixp_short[current + 1]))
            if (final1 == final2 and not flag) or (final1 != final2 and flag):
                return False
        return True

    def check_number(self, rule, expression, path_asn, current, i, encounter_type, str_to_chk):
        '''
        Checks the similarity of the concatenated numbers in case of AS_M keyword for consecutive hops in the path.
        Input:
            a) rule: The current rule.
            b) expression: The current condition of the condition part of the rule.
            c) path_asn: The AS path.
            d) current: The current hop in the path.
            e) i: The hop of the current condition in the rule.
            f) encounter_type: The resolved IP path based on the encountered types (IXP IP, IXP Prefix, Normal IP, Illegal IP).
            g) str_to_chk: The condition keyword of the rule.
            h) path: The current IP path.
        Output:
            True if the condition is satisfied, False otherwise.
        '''
        
        if len(rule) > i + 1 and len(path_asn) > current + 1:

            [final1, final2] = self.find_numbers(rule, str_to_chk, current, True)
            if final1 == '' or final2 == '':
                return True
            if self.is_int(final1) and self.is_int(final2):
                if (final1 == final2 and path_asn[current] != path_asn[current + 1]) or (final1 != final2 and path_asn[current] == path_asn[current + 1]):
                    return False
        return True

    def check_names(self, rule, expression, current, i, encounter_type, str_to_chk, ixp_long, ixp_short):
        '''
        Checks the similarity of the concatenated numbers in case of IXP_IP keyword for consecutive IXP IPs in the path.
        It also compares the IXP short and long names.
        Input:
            a) rule: The current rule.
            b) expression: The current condition of the condition part of the rule.
            c) i: The hop of the current condition in the rule.
            d) encounter_type: The resolved IP path based on the encountered types (IXP IP, IXP Prefix, Normal IP, Illegal IP).
            e) str_to_chk: The condition keyword of the rule.
            d) ixp_long,ixp_short: The IXP long and short names.
        Output:
            True if the condition is satisfied, False otherwise.
        '''
        
        string_handle = string_handler.string_handler()
        if len(rule) > i + 1 and len(ixp_long) > current + 1:
            [final1, final2] = self.find_numbers(
                rule, str_to_chk, current, True)
            if final1 == '' or final2 == '':
                return True
            if self.is_int(final1) and self.is_int(final2):
                flag = (string_handle.string_comparison(ixp_long[current], ixp_long[
                        current + 1]) or string_handle.string_comparison(ixp_short[current], ixp_short[current + 1]))
                if (final1 == final2 and not flag) or (final1 != final2 and flag):
                    return False

        return True

    def is_int(self, myint):
        '''
        Checks if the given string can be converted to an integer.
        Input:
            a) myint: The candidate string.
        Output:
            True if a string number can be converted to an integer, False otherwise.
        '''
        
        try:
            int(myint)
            return True
        except ValueError:
            return False

    def find_numbers(self, rule, str_to_chk, i, consecutive):
        '''
        Finds the concatenated numbers in keywords.
        Input:
            a) rule: The current rule.
            b) str_to_chk: The candidate keyword to check.
            c) i: The current part of the rule.
            d) consecutive: True for consecutive hops, False for border hops.
        Output:
            a) final1,final2: The concatenated numbers of the keywords.
        '''
        
        final1 = ''
        final2 = ''
        if consecutive:
            j = i + 1
        else:
            j = i + 2
        try:
            final1 = rule[i].split(str_to_chk)[1][:1]
            final2 = rule[j].split(str_to_chk)[1][:1]
        except:
            pass
        
        return (final1, final2)

    def load_syntax_rules(self, filename1, filename2, mypath):
        '''
        Loads the allowed rule keywords and the allowed delimeters between the keywords. It defines the syntax
        of the rules.
        Input:
            a) filename1: The expressions.txt file name.
            b) filename2: The delimeters.txt file name.
        Output:
            a) delimeters1: A list containing the delimeters that separate the keywords.
            b) expressions: A list containing the allowed keywords. 
        '''
        
        def load_files(filename):
            try:
                with open(filename) as f:
                    return [line.strip() for line in f.readlines()]
            except:
                print(filename + ' not found. Exiting.')
                sys.exit(0)

        expression_dump = load_files(mypath + '/' + filename1)
        delimiter_dump  = load_files(mypath + '/' + filename2)

        candidate_delimiters = [del_node.split('#')[0] for del_node in delimiter_dump if del_node.split('#')[0]]
        if len(candidate_delimiters) != 1:
            print('Expected one line of delimeters in ' +
                  filename2 + '. Exiting.')
            sys.exit(0)
            
        delimiters = [node for node in candidate_delimiters[0].split(',')]
        expressions = [ex_node.split('#')[0] for ex_node in expression_dump if ex_node.split('#')[0]]
       
        return (delimiters, expressions)

    def check_syntax_rules(self, cur_expression, expressions, delimiter):
        '''
        Validates a condition set in the rule.
        Input:
            a) cur_expression: The current expression.
            b) expressions: A list containing the allowed keywords. 
            c) delimeters1: A list containing the delimeters that separate the keywords.
        Output:
            a) True if the expression is valid, False otherwise.
        '''

        for node in delimiter:
            cur_expression = cur_expression.replace(node, 'cut')

        for node in cur_expression.split('cut'):
            if node not in expressions:
                return False
        return True
