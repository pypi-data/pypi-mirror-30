# goes-py 

 It's a free Python package to acess and get the dataset from GOES satellite next generation on Amazon Web Service(AWS)
 
 For more details, look at the online documentation (soon)

## HOWTO-Install 
 
 ### 1. Source code:
 
 If you want to build this package, just clone this repository:

 >**git clone git@github.com:palexandremello/goes-py.git**

 Go to folder:

>**cd goes-py** 

 And install manually

>**pip install -e .**

But if you don't want to build the cloned repository, just use the pip.

 ### 2. Pip Install: 
 
  With the pip:
  
  > **pip install goes-py**

 ## Examples how to use:

 This package has two main function, can be used to get dataset from GOES:

 ### 1. To use ABI-sensors:
 
> **from goes-py import ABI_Downloader**

The ABI_Downloder needs 7 arguments to be used:

>ABI_Downloader(bucket,year,month,day,hour,product,channel)

>bucket: name of reposity from GOES on the Amazon Web Service (AWS)
>year: year string 
>month: month string 
>day: day string
>hour: hour string, but it's need be UTC coordinate not local time
>product: "ABI-sensors" for this example we will use FullDisk L2
>channel: channels of your choose, can be C01 at C16

 ### 2. To GLM total lightning:
 
> **from goes-py import GLM_Downloader**

If you want you can run two examples on the folder **examples/** on the source directory:


 ## Contributors: 
 Centro de Pesquisas e Previsões Meteorológicas Prof. Darci Pegoraro Casarin ( <a href="https://wp.ufpel.edu.br/cppmet/">CPMET</a>) for the place and computers necessary to work on this project 

