DATE_COLUMNS = ['registration_date', 'operation_date']

dtypes = {
    'ИНН':'object',
    'СОАТО': 'object',
    'Тип т/с': 'category',
    'Код т/с': 'object',
    'Год':'str',
    
    'Максимальная масса': 'object',
    'Масса без нагрузки': 'object',
    
    'Мощность': 'object',
    'Первичность': 'object',
    'Принадлежность': 'object',
    'Тип кузова': 'object',
}

RUS2ENG_COL = {
    'ИНН': 'inn',
    'СОАТО': 'coato',
    'Тип т/с' : 'vehicle_type',
    'Дата регистрации' : 'registration_date',
    'Дата операции': 'operation_date',
    'Марка': 'brand',
    'Модель': 'model',
    'Класс': 'class',
    'Кол фор-ла': 'chassis_config',
    'Год' : 'year',
    'VIN' : 'vin',
    'Максимальная масса': 'mass_max', 
    'Масса без нагрузки': 'mass_idle',
    'Город': 'city',
    'Район': 'region',
    'сфера': 'activity_field',
    
    'Происхождение': 'origin',
    'Первичность': 'primary',
    'Принадлежность': 'affiliation',
    'Код т/с': 'code',
    'Тип кузова': 'body_type',
}
