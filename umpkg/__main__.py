#!/usr/bin/python3

import configparser
from multiprocessing.sharedctypes import Value
from arrow import parser
import koji
import typer
import os
import sys
import umpkg.cfg as config
import umpkg.util as util
import umpkg.rpm_util as rpm_util
import umpkg.koji_util as koji_util
import umpkg.repo as repo

cfg = config.read_config()
globalCfg = config.readGlobalConfig()

# if --version or -v is passed, print the version and exit
if "--version" in sys.argv or "-v" in sys.argv:
    # get the version from setup.py
    import pkg_resources

    info = pkg_resources.require("umpkg")[0]
    print(f"{info}, Copyright (c) 2021-22, Ultramarine Linux Team")
    sys.exit(0)

if "-h" in sys.argv:
    # convert it to --help
    sys.argv.remove("-h")
    sys.argv.append("--help")

app = typer.Typer()
app.add_typer(koji_util.app, name="koji", help="Koji build system commands")
app.add_typer(config.app, name="config", help="Configuration commands")
app.add_typer(repo.app, name="repo", help="Local Repository commands")


@app.command()
def buildsrc(
    path: str = typer.Argument(None, help="The path to the package"),
):
    """
    Builds a source RPM from a spec file
    """
    command = util.Command()
    if not path:
        # split the spec names by space
        specs = cfg["spec"].split(" ")
        for spec in specs:
            # add .spec to the spec name if it's not already there
            if not spec.endswith(".spec"):
                spec += ".spec"
            if os.path.exists(spec):
                srpm = command.buildSrc(spec)
            else:
                print(f"Spec {spec} not found")
                sys.exit(1)
    else:
        if not path.endswith(".spec"):
            path += ".spec"
        if os.path.exists(path):
            srpm = command.buildSrc(path)
        else:
            print(f"Spec {path} not found")
            sys.exit(1)


@app.command()
def build(
    path: str = typer.Argument(None, help="The path to the package"),
):
    """
    Builds a package from source
    """
    command = util.Command()
    if not path:
        # split the spec names by space
        specs = cfg["spec"].split(" ")
        for spec in specs:
            # add .spec to the spec name if it's not already there
            if not spec.endswith(".spec"):
                spec += ".spec"
            if os.path.exists(spec):
                srpm = command.buildSrc(spec)
            else:
                print(f"Spec {spec} not found")
                sys.exit(1)
    else:
        if not path.endswith(".spec"):
            path += ".spec"
        if os.path.exists(path):
            srpm = command.buildSrc(path)
        else:
            print(f"Spec {path} not found")
            sys.exit(1)

    # now build it using mock. sorry folks too lazy to do it properly
    builder = rpm_util.Mock()
    builder.buildRPM(srpm)


@app.command()
def push(
    tag: str = typer.Argument(..., help="The Koji tag to push"),
    branch: str = typer.Option(None, "--branch", "-b", help="The branch to push from"),
):
    """
    Pushes the current repo to Koji
    """
    command = util.Command()
    return command.push(tag, branch)


@app.command()
def get(
    name: str = typer.Argument(..., help="The package name"),
):
    """
    Gets the package source from Ultramarine GitLab
    """
    return util.Command.pullGitlab(None, project=name)


@app.command()
def help(
    name: str = typer.Argument(None, help="The command to get help for"),
):
    """
    Displays help for the specified command
    """
    if name is None:
        app(args=["--help"])
    else:
        app(args=[name, "--help"])


@app.command()
def init(
    spec: bool = typer.Option(None, "--spec", "-s", help="Initialize a spec file"),
):
    """
    Initializes a umcfg configuration file
    """
    # finish up
    # if spec is null, ask if they want to initialize a spec file
    if spec is None:
        # ask the user if they want to initialize a spec file
        print("Do you want to initialize a spec file?")
        print("[y/n]")
        while True:
            ans = input("> ")
            if ans == "y":
                # initialize a spec file
                spec = True
                break
            elif ans == "n":
                # don't initialize a spec file
                spec = False
                break
            else:
                print("Invalid input")
    # if spec is true, initialize a spec file
    if spec:
        # ask the user for the package name
        print("What will be the package name?")
        while True:
            name = input("> ")
            if name:
                break
            else:
                print("Invalid input")
        # run the init command
        os.system(f"rpmdev-newspec {name}")
    # read the local config file
    lcfg = config.defaults
    parser = configparser.ConfigParser()

    # add umcfg section
    parser.add_section("umpkg")
    for key, value in lcfg.items():
        if parser.has_option("umpkg", key):
            lcfg[key] = config.get("umpkg", key)
        else:
            parser.set("umpkg", key, value)
    # write the config file
    with open("umpkg.cfg", "w") as configfile:
        parser.write(configfile)
    # write a gitignore file
    with open(".gitignore", "w") as gitignore:
        gitignore.write("*.rpm\n")
        gitignore.write("*.src.rpm\n")
        gitignore.write("*.log\n")
        gitignore.write("build/\n")
        gitignore.write(".tar.*\n")


@app.callback()
def main(
    # version with alias of -v
    version: bool = typer.Option(False, "--version", "-v", help="Show the version"),
):
    """
    The Ultramarine Linux packager tool
    """
    if version:
        # get version from package's setup.py
        import setup

        print(setup.__version__)


if __name__ == "__main__":
    # run help if no arguments are passed
    if len(sys.argv) == 1:
        app(args=["--help"])
    else:
        app()

def entrypoint():
    if len(sys.argv) == 1:
        app(args=["--help"])
    else:
        app()
