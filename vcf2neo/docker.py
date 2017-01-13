"""
Interface to handle Docker
"""
import os
import random
import time
from shlex import shlex
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError, check_call

from tqdm import tqdm


class Docker(object):
    """
    Handle all docker processes.
    """

    # TODO: Where are we getting the reference database?
    def __init__(self, refdb_dir=None):
        self.name = "vcf2neo_" + str(random.randint(0, 1000))
        self.refdb_dir = refdb_dir
        self.container = None

    @staticmethod
    def new_split(value):
        lex = shlex(value)
        lex.quotes = '"'
        lex.whitespace_split = True
        lex.commenters = ''
        return list(lex)

    def run(self):
        """
        Start the Neo4j container.
        :return:
        """
        # TODO: Upgrade the IE image to Neo4j:3.0.x. Using 3.0.4 image for testing
        # cmd_str = "docker run --rm -P -v {refdb_dir}:/data/neo4jdb -e NEO4J_UID={uid} -e NEO4J_GID={gid} " \
        #           "-e NEO4J_AUTH=none -e NEO4J_MONITOR_TRAFFIC=false --name {name} thoba/neo4j_galaxy_ie:v1".format(
        #     refdb_dir=os.getcwd()+"/"+self.refdb_dir, name=self.name, uid=os.getuid(), gid=os.getgid())
        cmd_str = "docker run --rm -P -v {refdb_dir}:/data " \
                  "-e NEO4J_AUTH=none --name {name} neo4j:3.0.4".format(
            refdb_dir=os.getcwd() + "/" + self.refdb_dir, name=self.name, uid=os.getuid(), gid=os.getgid())
        cmd = self.new_split(cmd_str)
        print("Starting docker:\n{}...".format(cmd))
        try:
            self.container = Popen(cmd, stdout=PIPE, stderr=STDOUT)
            # TODO: Find a way to handle communicate
            # if self.container.communicate():
            #     print(self.container.communicate()[0])
            for i in tqdm(xrange(10), ascii=True, desc="Waiting for Neo4j"):
                time.sleep(1)
            print("Neo4j running!")
        except (OSError, ValueError) as e:
            print("Error running {}".format(self.name), e)
        finally:
            return True

    def port(self):
        """
        Find the container port.
        :return:
        """
        output = None
        cmd_str = "docker inspect " \
                  "--format='{{(index (index .NetworkSettings.Ports \"7474/tcp\") 0).HostPort}}' %s" % self.name
        try:
            output = check_output(cmd_str, shell=True)
        except CalledProcessError:
            print("Error running {} on {}".format(cmd_str, self.name))
            exit(1)
        return output

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
