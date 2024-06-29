The controller (Table entries generation module) requires Python2.7. The latest P4 behavior model version requires Python3.x, so we recommend conda to manage environments. We feel sorry for such inconvenience and will migrate to full python3.X as soon as possible.

In Python 2.7, here are the prerequisites.

```bash
conda create -n python27 python=27 
pip install pyahocorasick 
```

### Data plane

Build the [P4 tutorial VM]("https://github.com/p4lang/tutorials"), and move the dir `BOLT` into `tutorials/exercise/`.

## Running

### Generating table entries

In python2.7 environment, run `Controller.py`:

```bash
(python27) python Controller.py
```

It will generate the p4 spec file in `*-runtime.json`, which contains the table entries about the rule set.

### Sending packet

1. Run the switch:

    ```bash
    make run
    ```
    
2. In the Mininet shell, invoke the xterm console for simulated host  `h1` and `h2`:

    ```bash
    mininet> xterm h1 h2
    ```

    Sniff the packets in `h2`:

    ```bash
    python recv.py
    ```

    Send packets conataining crafted payload in `h1`:

    ```bash
    python send.py 10.0.2.2 U "abc"
    ```

    `h2` displays a packet with srcport set as `2010`, which means a rule is hit.

    ```bash
    python send.py 10.0.2.2 U "abdm"
    ```

    `h2` displays a packet with srcport set as `1024`, which means a bucket get overwritten.

