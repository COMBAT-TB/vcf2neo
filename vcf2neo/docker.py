"""
Interface to handle Docker
"""
import os
import random
import shlex
from subprocess import Popen, PIPE, STDOUT, check_output, \
    CalledProcessError, check_call
import sys
import time

try:
    from io import StringIO
except:
    from StringIO import StringIO

from tqdm import tqdm


class Docker(object):
    WORDS = ['again', 'ages', 'almost', 'america', 'ancient', 'another',
             'antagonisms', 'apprentices', 'armies', 'arrangement', 'away',
             'background', 'before', 'between', 'bourgeois', 'bourgeoisie',
             'burgesses', 'burghers', 'camps', 'cape', 'capital', 'carried',
             'chartered', 'chinese', 'class', 'classes', 'closed', 'colonies',
             'colonisation', 'commerce', 'commodities',
             'common', 'communication',
             'complicated', 'conditions',
             'constant', 'contending', 'corporate',
             'course', 'demand', 'developed', 'development', 'different',
             'directly', 'discovery', 'distinct', 'division', 'done', 'down',
             'each', 'earlier', 'earliest', 'eastindian', 'either', 'element',
             'elements', 'ended', 'epoch', 'epochs',
             'established', 'even', 'ever',
             'every', 'everywhere', 'exchange', 'existing', 'extended',
             'extension', 'face', 'facing', 'feature',
             'feudal', 'fight', 'find',
             'first', 'forms', 'freeman', 'fresh', 'from', 'gave', 'generally',
             'giant', 'given', 'gradation', 'gradations', 'great', 'ground',
             'growing', 'guildmaster', 'guildmasters',
             'guilds', 'handed', 'have',
             'hidden', 'history', 'hitherto', 'hostile', 'however', 'immense',
             'impulse', 'increase', 'increased',
             'industrial', 'industry', 'into',
             'itself', 'journeyman', 'journeymen', 'kept', 'knights', 'known',
             'labour', 'land', 'large', 'leaders', 'long', 'longer', 'lord',
             'lords', 'machinery', 'manifold', 'manufacture', 'manufacturer',
             'manufacturing', 'market', 'markets',
             'means', 'meantime', 'middle',
             'millionaires', 'modern', 'modes', 'monopolised', 'more',
             'navigation', 'never', 'ones', 'open', 'opened', 'opposition',
             'oppressed', 'oppression', 'oppressor', 'orders', 'other',
             'patrician', 'patricians', 'paved',
             'place', 'plebeian', 'plebeians',
             'possesses', 'product', 'production', 'proletariat', 'proportion',
             'pushed', 'railways', 'rank', 'rapid',
             'reacted', 'reconstitution',
             'revolutionary', 'revolutionised',
             'revolutions', 'rising', 'rome',
             'rounding', 'ruin', 'ruins', 'same', 'serf', 'serfs', 'series',
             'side', 'simplified', 'single', 'slave', 'slaves', 'social',
             'society', 'splitting', 'sprang', 'sprouted', 'steam', 'stood',
             'struggle', 'struggles', 'subordinate',
             'sufficed', 'system', 'taken',
             'that', 'thereby', 'therefore', 'thereupon',
             'these', 'this', 'time',
             'took', 'tottering', 'towns', 'trade', 'turn', 'uninterrupted',
             'vanished', 'various', 'vassals', 'wants',
             'were', 'which', 'whole',
             'with', 'word', 'workshop', 'world']

    """
    Handle all docker processes.
    """

    # TODO: Where are we getting the reference database?
    def __init__(self, outputdir, use_bolt=False, image_name='quay.io/sanbi-sa/neo_ie:3.1'):
        self.name = '_'.join(['vcf2neo', random.choice(self.__class__.WORDS), random.choice(self.__class__.WORDS)])
        self.outputdir = outputdir
        self.container = None
        self.use_bolt = use_bolt
        self.image_name = image_name

    @staticmethod
    def new_split(value):
        lex = shlex.shlex(value)
        lex.quotes = '"'
        lex.whitespace_split = True
        lex.commenters = ''
        return list(lex)

    def run(self):
        """
        Start the Neo4j container.
        :return:
        """
        if self.use_bolt:
            bolt_string = ' -e ENABLE_BOLT=true '
        else:
            bolt_string = ''
        cmd_str = "docker run --rm -v {outputdir}:/data -p 7474 -p 7687 " \
                  "-e USER_UID={uid} -e USER_GID={gid} " \
                  "-e MONITOR_TRAFFIC=false {bolt} " \
                  "-e NEO4J_AUTH=none --name {name} " \
                  "{image_name}".format(outputdir=self.outputdir, bolt=bolt_string, uid=os.getuid(), gid=os.getgid(),
                                        name=self.name, image_name=self.image_name)
        cmd = self.new_split(cmd_str)
        sys.stderr.write("Starting docker:\n{}...".format(cmd))
        print("Starting docker:\n{}...".format(cmd))
        try:
            self.container = Popen(cmd, stdout=PIPE, stderr=STDOUT)
            # TODO: Find a way to handle communicate
            # if self.container.communicate():
            #     print(self.container.communicate()[0])
            for i in tqdm(range(15), ascii=True, desc="Waiting for Neo4j"):
                time.sleep(1)
            sys.stdout.write("Neo4j running!")
            print("Neo4j running!")
        except (OSError, ValueError) as e:
            sys.stderr.write("Error running {}:\n{}".format(self.name, e))
            print("Error running {}:\n{}".format(self.name), e)
        self.find_docker_portmapping()
        return True

    def find_docker_portmapping(self):
        cmd_str = "docker port {}".format(self.name)
        cmd = shlex.split(cmd_str)
        output = check_output(cmd)
        port_mapping = dict()
        for line in StringIO(output.decode("utf-8")):
            (dest_str, src_str) = line.split(' -> ')
            # print(dest_str.split('/'))
            dest_port = int(dest_str.split('/')[0])
            src_port = int(src_str.split(':')[1])
            port_mapping[dest_port] = src_port
        assert 7474 in port_mapping, "Could not find HTTP port"
        assert 7687 in port_mapping, "Could not find Bolt port"
        self.http_port = port_mapping[7474]
        self.bolt_port = port_mapping[7687]

    def stop(self):
        """
        Stop the container
        :return:
        """
        cmd_str = "docker stop {}".format(self.name)
        cmd = self.new_split(cmd_str)
        try:
            check_call(cmd)
        except CalledProcessError:
            print("Error running: docker stop {}".format(self.name))
            exit(1)
        print("Successfully stopped {}!".format(self.name))
        return True
