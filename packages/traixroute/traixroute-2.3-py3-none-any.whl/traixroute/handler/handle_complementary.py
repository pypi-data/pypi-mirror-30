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

from traixroute.downloader import download_files
from traixroute.controller import string_handler
from shutil import copyfile
import sys
import os
import SubnetTree


class asn_handle():
    '''
    Handles the AS prefixes from Routeviews.
    '''

    def __init__(self, downloader, libpath):
        self.route_filename = '/RouteViews/routeviews'
        self.downloader     = downloader
        self.homepath       = downloader.getDestinationPath()
        self.libpath        = libpath

    def routeviews_extract(self, reserved_sub_tree):
        '''
        Imports the file from routeviews to a Subnet Tree.
        Input:
            a) filename: The file name from routeviews to parse.
            b) mypath: The directory path of the database folder.
            c) reserved_sub_tree: The SubnetTree containing the reserved Subnets.
            d) config: Dictionary that contains the config file.
            e) db_path: The path to the Database directory.
        Output: 
            a) Stree: A SubnetTree containing IXP Subnet-to-ASNs.
            b) temp_dict: A dictionary containing {IXP Subnet} = AS.
        '''

        handler = string_handler.string_handler()
        try:
            f = open(self.homepath + '/database' + self.route_filename)
        except:
            print(self.route_filename + ' was not found.')
            if not self.downloader.download_routeviews():
                print("Could not download " + self.route_filename +
                      ". Copying from the default database.")
                try:
                    copyfile(self.libpath + '/database/Default' + self.route_filename,
                             self.homepath + '/database' + self.route_filename)
                except:
                    print('Could not copy ' + self.route_filename +
                          ' from the default database.')
            try:
                f = open(self.homepath + '/database' + self.route_filename)
            except:
                print('Could not open ' + self.route_filename + '. Exiting.')
                sys.exit(0)

        temp_dict = {}
        Stree = SubnetTree.SubnetTree()
        for line in f:
            temp = line.split()
            myip = handler.extract_ip(temp[0], 'IP')
            if len(myip):
                if handler.is_valid_ip_address(myip[0] + '/' + temp[1], 'Subnet', 'RouteViews'):
                    if not handler.sub_prefix_check(myip[0] + '/' + temp[1], reserved_sub_tree):
                        Stree[myip[0] + '/' + temp[1]]     = temp[2]
                        temp_dict[myip[0] + '/' + temp[1]] = temp[2]

        f.close()
        return Stree, temp_dict


class asn_memb_info():
    '''
    Handles the AS Membership information.
    '''

    def asn_memb(self, IXP_final, sub2names):
        '''
        Constructs a new dictionary with {ASN}={IXP long name, IXP short name} based on IXP_final and dirty_ixp2asn dictionaries.
        Input:
            a) IXP_final: A dictionary with {IXP IP}=[ASN] after merging peeringdb and pch datasets.
            c) sub2names: The SubnetTree with the IXP prefixes to a list of [IXP long name, short name].
        Output:
            a) asn_member2ixpname: A dictionary with {ASN}=[IXP long name, IXP short name].
        '''

        asn_member2ixpname = {}
        for node in IXP_final:
            new_key = IXP_final[node][0]
            temp_string_node = sub2names[node]

            if new_key not in asn_member2ixpname:
                asn_member2ixpname[new_key] = []
                
            for IXP in temp_string_node:
                asn_member2ixpname[new_key].append(IXP)

        return asn_member2ixpname


class reserved_handle():
    '''
    Handles the reserved IPs.
    '''

    def __init__(self):
        # self.reserved_list: A list with the reserved list.
        self.reserved_list = [
            '0.0.0.0/8', 
            '10.0.0.0/8', 
            '100.64.0.0/10',
            '127.0.0.0/8',
            '169.254.0.0/16', 
            '172.16.0.0/12', 
            '192.0.0.0/24', 
            '192.0.2.0/24',
            '192.88.99.0/24',
            '192.168.0.0/16',
            '198.18.0.0/15',
            '198.51.100.0/24',
            '203.0.113.0/24',
            '224.0.0.0/4',
            '240.0.0.0/4',
            '255.255.255.255/32']
    
        # self.reserved_sub_tree: A Subnet Tree with the reserved subnets.
        self.reserved_sub_tree = SubnetTree.SubnetTree()

    def reserved_extract(self):
        '''
        Loads the reserved subnets in a SubnetTree data structure to easily sanitize the total data in the database.
        '''

        for node in self.reserved_list:
            self.reserved_sub_tree[node] = node


class Subnet_handle():
    '''
    Imports the extracted IXP Subnets to a Subnet Tree.
    '''

    def Subnet_tree(self, Sub, additional_tree, reserved_sub_tree, final_subnet2country):
        '''
        Returns a Subnet Tree containing all the IXP subnets.
        Input:
            a) Sub: A dictionary with {Subnet}=[IXP long name,IXP short name] after merging PDB and PCH datasets.
            b) additional_tree: a Subnet Tree containing all the user {IXP Subnet}=IXP Subnet.
            c) reserved_sub_tree: A SubnetTree containing the reserved Subnets.
            d) final_subnet2country: A dictionary with {Subnet}=[country,city].
        Output:
            a) Stree: A Subnet Tree with the IXP names.
            b) Sub: A dictionary with {Subnet}=[IXP long name,IXP short name].
            c) help_tree: A Subnet Tree with IXP Subnets.
        '''

        Stree = SubnetTree.SubnetTree()
        help_tree = SubnetTree.SubnetTree()
        handle_string = string_handler.string_handler()
        
        for subnet in sorted(Sub):
            check = handle_string.sub_prefix_check(subnet, help_tree)
            
            # If a subprefix does not exist and it is not a reserved prefix.
            if not check and not handle_string.sub_prefix_check(subnet, additional_tree) and not handle_string.sub_prefix_check(subnet, reserved_sub_tree):
                Stree[subnet] = Sub[subnet]
                help_tree[subnet] = subnet
            # If a subprefix exists.
            elif check:
                # Keep initial tuple to find the corresponding prefix in order to keep only prefix in the last step.
                initial_tuple = Stree[subnet]
                # Find the prefix that maps to the initial tuple in order to keep the prefix, update the IXP names and delete subprefix in the last step.
                prefix = [temp_subnet for temp_subnet, temp_ixp_name in Sub.items() if temp_ixp_name == initial_tuple][0]
                
                # Gather the IXP names of existing subprefixes in the Subnet Tree.
                assign_tuple = []
                for IXP1 in Stree[subnet]:
                    for IXP2 in Sub[subnet]:
                        assign_tuple = assign_tuple + handle_string.assign_names(
                                IXP1[1], IXP2[1], IXP1[0], IXP2[0])
                
                # Delete similar IXP names assigned to the same prefixes.
                deleted = []
                for i in range(0, len(assign_tuple) - 1):
                    for j in range(i + 1, len(assign_tuple)):
                        if len(handle_string.assign_names(assign_tuple[i][0], assign_tuple[j][0], assign_tuple[i][1], assign_tuple[j][1])) == 1:
                            if j not in deleted:
                                deleted = [j] + deleted
                for node in deleted:
                    del assign_tuple[node]

                # Delete Subprefixes when there are Prefixes with same IXP names.
                if assign_tuple == Stree[subnet]:
                    Sub.pop(subnet)
                    final_subnet2country.pop(subnet)
                # Keep Prefixes (as dirty) and delete Subprefixes with different IXP names.
                else:
                    # Update prefix with the new IXP names
                    Stree[prefix]     = assign_tuple
                    Sub[prefix]       = assign_tuple
                    # Delete subprefix
                    Sub.pop(subnet)
                    final_subnet2country.pop(subnet)
            else:
                Sub.pop(subnet)
                final_subnet2country.pop(subnet)
        
        return Stree, Sub, help_tree

    def exclude_reserved_subpref(self, subTree, final_sub2name, reserved_list, final_subnet2country):
        '''
        Excludes the reserved subprefixes.
        Input:
            a) subTree: The SubnetTree containing [[IXP long name, IXP short name]].
            b) final_sub2name: The dictionary with {IXP Subnet} = [[IXP long name, IXP short name]].
            c) reserved_list: A list containing the reserved prefixes.
            d) final_subnet2country: A dictioanry containing {IXP Subnet} = [ IXP country, IXP city].
        Output:
            a) subTree: The SubnetTree containing [[IXP long name, IXP short name]].
            b) final_sub2name: The cleaned dictionary with {IXP Subnet} = [[IXP long name, IXP short name]].
        '''

        handle_string = string_handler.string_handler()
        for prefix in reserved_list:
            if handle_string.sub_prefix_check(prefix, subTree):
                rprefix = subTree[prefix]
                subTree.remove(rprefix)
                final_sub2name.pop(rprefix)
                final_subnet2country.pop(rprefix)
        return (subTree, final_sub2name)


class extract_additional_info():
    '''
    This class extracts additional IXP related information provided by the user.
    '''

    def __init__(self):

        # IXP_dict: A dictionary with {IXP IP}=[ASN].
        self.ixp_ip2asn = {}
        # Subnet: A dictionary with {Subnet}=[IXP long name,IXP short name].
        self.Subnet = {}
        # additional_info_tree: A Subnet Tree containing all the IXP subnets
        # provided by the user.
        self.additional_info_tree = SubnetTree.SubnetTree()
        # pfx2cc: A Dictionary containing all the IXP subnets or IPs to cities
        # provided by the user.
        self.pfx2cc = {}
        # additional_info_help_tree: A subnetTree containing [IXP Subnet]=IXP
        # Subnet
        self.additional_info_help_tree = SubnetTree.SubnetTree()
        # The filename in which a user can add its own IXP IPs/Prefixes.
        self.user_ixps_filename = 'additional_info.txt'

    def extract_additional_info(self, mypath):
        '''
        Input: 
            a) filename: the additional_info.txt file.
        '''

        mypath += '/configuration/' + self.user_ixps_filename
        handles = string_handler.string_handler()

        # Creates the user IXP file if it does not exist.
        if not os.path.exists(mypath):
            try:
                f = open(mypath, 'a')
                f.close()
            except:
                print('Could not create ' + mypath + '.exiting.')
                sys.exit(0)
        else:
            with open(mypath, 'r') as f:

                # Parses the additional_info.txt file.
                i = 0
                for line in f:
                    i += 1
                    
                    # Ignores lines with comments.
                    if line.startswith('#'):
                        continue

                    line_split = [line.strip() for line in line.split(', ')]

                    IXP = handles.extract_ip(line, 'Subnet')
                    IXP = IXP[0] if len(IXP) else ''
                    
                    # Imports only IXP Subnets with valid format.
                    if handles.is_valid_ip_address(IXP, 'Subnet', 'Additional') and IXP == line_split[0]:
                        if len(line_split) == 5:

                            ixp_short_name  = line_split[1]
                            ixp_full_name   = line_split[2]
                            country         = line_split[3]
                            city            = line_split[4]
                            
                            if IXP not in self.Subnet.keys():
                                self.additional_info_tree[IXP]      = [ixp_full_name, ixp_short_name]
                                self.additional_info_help_tree[IXP] = IXP
                                self.Subnet[IXP]                    = [ixp_full_name, ixp_short_name]
                                self.pfx2cc[IXP]                    = [country, city]
                            else:
                                print(
                                    'additional_info.txt: Multiple similar IXP Prefixes detected. Exiting.')
                                sys.exit(0)
                        else:
                            print('Invalid syntax in line ' + str(i) + '. Exiting.')
                            sys.exit(0)
                    # Imports only IXP IPs with valid format.
                    else:
                        IXP = handles.extract_ip(line, 'IP')
                        IXP = IXP[0] if len(IXP) else ''
                            
                        if len(line_split) == 6:
                            try:
                                int(line_split[1])
                            except:
                                print('additional_info.txt: Invalid syntax in line ' + str(i) + '. Exiting.')
                                sys.exit(0)
                            asn             = line_split[1]
                            ixp_short_name  = line_split[2]
                            ixp_full_name   = line_split[3]
                            country         = line_split[4]
                            city            = line_split[5]
                            
                            if handles.is_valid_ip_address(IXP, 'IP', 'Additional'):
                                if IXP not in self.ixp_ip2asn:
                                    self.ixp_ip2asn[IXP]     = [asn]
                                    self.Subnet[IXP + '/32'] = [ixp_short_name, ixp_full_name]
                                    self.pfx2cc[IXP + '/32'] = [country, city]
                                else:
                                    print(
                                        'additional_info.txt: Multiple similar IXP IPs detected. Exiting.')
                                    sys.exit(0)
                            else:
                                print(
                                    'additional_info.txt: Invalid IP in line ' + str(i) + '. Exiting.')
                                sys.exit(0)
                        else:
                            print(
                                'additional_info.txt: Invalid syntax in line ' + str(i) + '. Exiting.')
                            sys.exit(0)
