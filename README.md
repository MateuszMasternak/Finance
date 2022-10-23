# Finance
</br>

## 🎥Demo:
![](https://j.gifs.com/LZzZVD.gif)
</br>
</br>

## ⚙️Stack:
<img src="https://user-images.githubusercontent.com/113989577/195915225-f7a51108-c25f-4e79-9b4e-77e90f3e6499.png" width="50"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Flask_logo.svg/1280px-Flask_logo.svg.png" width="120">
<br>
</br>

## 📄About:
Web app based on Flask. You can there check a price of stocks, "buy" them, "sell" that you already own, also check history of transactions. All the data about stocks is received via IEX's API.
</br>
</br>

## ⌨️How to run the app locally:
* Clone the repository.
* Download Python 3.\*.\*.
> https://www.python.org/downloads/.
* Create virtual environment:
> https://docs.python.org/3/tutorial/venv.html.
* Download all dependencies:
> python -m pip install -r requirements.txt.
* Register on the IEX's site:
> https://iexcloud.io/cloud-login#/register/
* Get your token:
> https://iexcloud.io/console/tokens
* Create .env file and type in "API_KEY='<your token>'" and "DB_NAME='<name of database>'" there. 
* Run the app via terminal form the main directory:
> flask --app application.py run
</br>
That's it.
