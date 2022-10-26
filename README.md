# Finance
</br>

## 🎥Demo:
![](https://j.gifs.com/LZzZVD.gif)
</br>
</br>

## ⚙️Stack:
<img src="https://user-images.githubusercontent.com/113989577/195915225-f7a51108-c25f-4e79-9b4e-77e90f3e6499.png" width="50"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Flask_logo.svg/1280px-Flask_logo.svg.png" width="120"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Sqlite-square-icon.svg/2048px-Sqlite-square-icon.svg.png" width="45"> <img src="https://user-images.githubusercontent.com/113989577/195917268-9fc749f5-9a72-4375-9c7d-8520dcfa4c5f.png" width="50"> <img src="https://user-images.githubusercontent.com/113989577/195917361-c0afb3bb-06c3-458c-9f64-41444f3f4300.png" width="50"> <img src="https://user-images.githubusercontent.com/113989577/195927768-05a81249-e2c7-409a-8435-692b338c8d31.png" width="50">
<br>
</br>

## 📄About:
Finance is a stock exchange web app based on flask. The app enables to check a price of stocks, "buy" them, "sell" those you already own, also check history of transactions. All the data about the stocks is delivered via IEX's API.
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
