# -*- coding: utf-8 -*-
import sys
from .client import Client


def main():
    try:
        Client().main(sys.argv[1:])
        # Client().main(["deploy", "-h"])
        # Client().main(["ls", "cluster", "--clusterid", "c6"])
        # Client().main(["ls", "cluster"])
        # Client().main(["ls", "machine", "--machineid", "cn6"])
        # Client().main(["ls", "machine", "--clusterid", "c1"])
        # Client().main(["ls", "machine"])
        # Client().main(["ls", "application"])
        # Client().main(["ls", "application", "--appid", "a1"])
        # Client().main(["ls", "application", "--clusterid", "c1"])
        # Client().main(["ls", "service", "--appid", "a76"])
        # Client().main(["ls", "task", "--appid", "a1"])
        # Client().main(["ls", "microservice"])
        # Client().main(["ls", "microservice", "--serviceid", "s232"])
        # Client().main(["ls", "instance", "--serviceid", "s230"])
        # Client().main(["ls", "instance_log", "--serviceid", "s230", "--instanceid", "i445"])
        # Client().main(["statistics", "cluster"])
        # Client().main(["statistics", "cluster", "--clusterid", "c1"])
        # Client().main(["statistics", "machine"])
        # Client().main(["statistics", "application"])
        # Client().main(["statistics", "application", "--appid", "a3"])
        # Client().main(["statistics", "microservice", "-h"])
        # Client().main(["statistics", "microservice", "--serviceid", "s232"])
        # Client().main(["undeploy", "service", "--serviceid", "s333", "--appid", "a76"])
        # Client().main(["deploy", "service", "--serviceid", "s334", "--appid", "a76"])
        # Client().main(["deploy", "instance", "--serviceid", "s333", "--microserviceid", "ms608", "--instanceid", "i584", "i581"])
        # Client().main(["delete", "instance", "--serviceid", "s334", "--microserviceid", "ms612" , "--instanceid", "i597"])
        # Client().main(["login", "-u", "sanghong", "-p", "sanghong", "-d", "huayun.com"])
        # Client().main(["login", "-u", "sanghong", "-p", "sanghong"])
        # Client().main(["login", "-h"])
        # Client().main(["logout"])
    except Exception as e:
        msg = e.message
        if not msg or msg == '':
            msg = e.strerror
        # print "ERROR: %s" % msg
        print msg
        sys.exit(1)

if __name__ == "__main__":
    main()
