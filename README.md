## Телеграм бот
Целью данного проекта является создание телеграм-бота, который предоставляет текущую погоду и прогноз на определенный период 
времени для указанного города. Бот будет использовать API OpenWeather для получения актуальных метеорологических данных.

### Используемые Endpoint'ы OpenWeather API:

* Получение координат: http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&limit={limit}&appid=ru&hl=ru&prev=search&u=https://home.openweathermap.org/api_keys"target
* Получение погоды в определенную дату: https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&appid={api_key}&units=metric'
* Получение погоды в данный момент: https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}

### План выполнения:

1. Подготовка IDE
2. Создание структуры бота
3. Получение ключей: BotFather, OpenWeather API
4. Реализация стандартных команд: /start, /help; проверка работоспособности бота
5. Реализация команды для получения прогноза погоды в данный момент
6. Реализация команды для получения прогноза погоды на 5 дней
7. Реализация команды для получения прогноза погоды в выбранную дату
8. Сдача проекта