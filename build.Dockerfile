# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

FROM debian:10.5-slim

RUN \
    apt-get update \
    && apt-get install \
        -y \
        python3=3.7.3-1 \
        python3-pip=18.1-5
