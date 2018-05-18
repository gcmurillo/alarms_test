angular.module('MyApp', ['ngMaterial'])
  .controller("side_bar", function($scope, $mdSidenav) {
    $scope.title = 'Alarms';
    $scope.toggleAlarms = buildToggler('alarms');
    $scope.toggleNotifications = buildToggler('notifications');
    $scope.toggleMenu = buildToggler('lateral_menu');

    function buildToggler(componentId) {
      return function() {
        $mdSidenav(componentId).toggle();
      };
    }

});

