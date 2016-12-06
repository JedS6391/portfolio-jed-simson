Title:   MINIX Journaled File System
Summary: Thoughts about implementing Journaling for the MINIX File System
Author:  Jed Simson
Date:    October 15, 2016
Tags:    File Systems, Journaling, MINIX, Journal, JFS, Project, University

In my second semester of 2016 I took a paper titled **Operating Systems**, which is a 300 level paper that deals with Operating Systems concepts and design. The majority of this paper focuses on the [MINIX](https://en.wikipedia.org/wiki/MINIX) OS to provide examples of design decisions (e.g. microkernel vs. monolithic kernel) and as the system is reasonably small and manageable (relative to something like Linux) it allows for the code to be analysed and modified to learn more about it.

A core component of this paper is what is called the MINIX Project, where one must decide on some extension to add to the MINIX system and implement it as a way of demonstrate understanding of the system and to gain experience working on a large system like that of an OS. The project is worth 50% and spans across about 2 months or so.

For my project I chose to extend the existing MINIX File System to include [journaling](https://en.wikipedia.org/wiki/Journaling_file_system), ultimately turning it into a reliable, journaling file system. I learnt a lot while working on this project and consider it one of the most complex projects I have worked on while studying at university.

The source for my project can be found in a GitLab repository [here](https://gitlab.com/JedS6391/COMP301-Project), and contains:

- Changes and additions to allow journaling within the existing file system
- Some tools for verification that the extension is working correctly
- A report detailing the implementation and some other components of the project. 

The version of MINIX used is 3.1.0.
