# type: ignore[attr-defined]

import random
import time
from enum import Enum
from multiprocessing import Pool
from os import sched_getaffinity
from pathlib import Path
from typing import List, Optional

import numpy as np
import typer
from rich.console import Console

from lindemann import __version__
from lindemann.example import hello
from lindemann.index import mem_use, per_atoms, per_frames, per_trj
from lindemann.trajectory import plt_plot, read, save

app = typer.Typer(
    name="lindemann",
    help="lindemann is a python package to calculate the Lindemann index  of a lammps trajectory as well as the progression of the Lindemann index per frame of temperature ramps  for phase transition analysis.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Prints the version of the package."""
    if value:
        console.print(
            f"[magenta]lindemann[/] version: [bold blue]{__version__}[/]"
        )
        raise typer.Exit()


@app.command(name="")
def main(
    trjfile: List[Path],
    trj: bool = typer.Option(
        False,
        "-t",
        help="Calculates the Lindemann-Index for the Trajectory file",
    ),
    frames: bool = typer.Option(
        False, "-f", help="Calculates the Lindemann-Index for each frame."
    ),
    atoms: bool = typer.Option(
        False,
        "-a",
        help="Calculates the Lindemann-Index for each atom for each frame.",
    ),
    plot: bool = typer.Option(
        False, "-p", help="Returns a plot Lindemann-Index vs. Frame."
    ),
    lammpstrj: bool = typer.Option(
        False,
        "-l",
        help="Saves the individual Lindemann-Index of each Atom in a lammpstrj, so it can be viewed in Ovito.",
    ),
    version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the lindemann package.",
    ),
    timeit: bool = typer.Option(
        False, "-ti", "-timeit", help="Uses timeit module to show running time",
    ),
    mem_useage: bool = typer.Option(
        False,
        "-m",
        "-mem_use",
        help="Calculates the memory use. Run it before you use any of the cli functionality despite the -t flag",
    ),
):

    """
    lindemann is a python package to calculate the Lindemann index  of a lammps trajectory as well as the progression of the Lindemann index per frame of temperature ramps  for phase transition analysis.
    """
    # frames = read.frames(trjfile)
    # frames = lindemann.trajectory.read.frames(trjfile)
    start = time.time()

    n_cores = len(sched_getaffinity(0))
    len_trjfiles = len(trjfile)

    if len_trjfiles > n_cores:
        n_cores = n_cores
    else:
        n_cores = len_trjfiles

    if len(trjfile) == 1:
        single_process = True
        tjr_frames = read.frames(str(trjfile[0]))
    else:
        single_process = False
        trjfile = [str(trjf) for trjf in trjfile]
        tjr_frames = [read.frames(tf) for tf in trjfile]

    if trj and single_process:

        console.print(
            f"[magenta]lindemann index for the Trajectory:[/] [bold blue]{per_trj.calculate(tjr_frames)}[/]"
        )
        raise typer.Exit()
    if trj and not single_process:
        with Pool(n_cores) as p:
            console.print(f"Using {n_cores} cores")
            res = p.map(per_trj.calculate, tjr_frames)
            console.print(res)
        raise typer.Exit()

    if frames and single_process:
        my_file_name = False
        if my_file_name:
            print("not implemented")
        else:
            filename = "lindemann_per_frame.txt"
        np.savetxt(filename, per_frames.calculate(tjr_frames))
        console.print(
            f"[magenta]lindemann index per frame saved as:[/] [bold blue]{filename}[/]"
        )
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()

    if atoms and single_process:
        filename = "lindemann_per_atom.txt"
        np.savetxt(filename, per_atoms.calculate(tjr_frames))
        console.print(
            f"[magenta]lindemann index per atoms saved as:[/] [bold blue]{filename}[/]"
        )
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()

    if plot and single_process:
        indices = per_frames.calculate(tjr_frames)

        console.print(
            f"[magenta]Saved file as:[/] [bold blue]{plt_plot.lindemann_vs_frames(indices)}[/]"
        )
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()

    if lammpstrj and single_process:
        indices_per_atom = per_atoms.calculate(tjr_frames)

        console.print(f"[magenta]{save.to_lammps(trjfile,indices_per_atom)}[/]")
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()

    if timeit and single_process:

        linde_for_time = per_trj.calculate(tjr_frames)
        time_diff = time.time() - start
        console.print(
            f"[magenta]lindemann index for the Trajectory:[/] [bold blue]{linde_for_time}[/] \n[magenta]Runtime:[/] [bold green]{time_diff}[/]"
        )
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()

    if mem_useage and single_process:

        mem_use_in_gb = mem_use.in_gb(tjr_frames)

        console.print(f"[magenta]memory use:[/] [bold blue]{mem_use_in_gb}[/]")
        raise typer.Exit()
    else:
        print("multiprocessing is implemented only for the -t flag")
        raise typer.Exit()
