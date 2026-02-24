package com.gruha.alankara.ui.navigation

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument
import com.gruha.alankara.ui.ar.ARScreen
import com.gruha.alankara.ui.auth.AuthViewModel
import com.gruha.alankara.ui.auth.LoginScreen
import com.gruha.alankara.ui.auth.RegisterScreen
import com.gruha.alankara.ui.home.HomeScreen

object Routes {
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val HOME = "home"
    const val AR_SCREEN = "ar_screen"
}

@Composable
fun NavGraph(
    navController: NavHostController = rememberNavController(),
    authViewModel: AuthViewModel = hiltViewModel(),
    startDestination: String = Routes.LOGIN
) {
    val authState by authViewModel.uiState.collectAsStateWithLifecycle()

    NavHost(
        navController = navController,
        startDestination = if (authState.isLoggedIn) Routes.HOME else startDestination,
        enterTransition = {
            fadeIn(animationSpec = tween(300)) + slideInHorizontally(
                initialOffsetX = { it / 4 },
                animationSpec = tween(300)
            )
        },
        exitTransition = {
            fadeOut(animationSpec = tween(300)) + slideOutHorizontally(
                targetOffsetX = { -it / 4 },
                animationSpec = tween(300)
            )
        },
        popEnterTransition = {
            fadeIn(animationSpec = tween(300)) + slideInHorizontally(
                initialOffsetX = { -it / 4 },
                animationSpec = tween(300)
            )
        },
        popExitTransition = {
            fadeOut(animationSpec = tween(300)) + slideOutHorizontally(
                targetOffsetX = { it / 4 },
                animationSpec = tween(300)
            )
        }
    ) {
        composable(Routes.LOGIN) {
            LoginScreen(
                uiState = authState,
                onEmailChanged = authViewModel::onEmailChanged,
                onPasswordChanged = authViewModel::onPasswordChanged,
                onLoginClick = {
                    authViewModel.login()
                },
                onNavigateToRegister = {
                    navController.navigate(Routes.REGISTER)
                }
            )

            // Navigate to Home when logged in
            LaunchedEffect(authState.isLoggedIn) {
                if (authState.isLoggedIn) {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            }
        }

        composable(Routes.REGISTER) {
            RegisterScreen(
                uiState = authState,
                onNameChanged = authViewModel::onNameChanged,
                onEmailChanged = authViewModel::onEmailChanged,
                onPasswordChanged = authViewModel::onPasswordChanged,
                onConfirmPasswordChanged = authViewModel::onConfirmPasswordChanged,
                onRegisterClick = {
                    authViewModel.register()
                },
                onNavigateToLogin = {
                    navController.popBackStack()
                }
            )

            // Navigate to Home when logged in
            LaunchedEffect(authState.isLoggedIn) {
                if (authState.isLoggedIn) {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            }
        }

        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToAR = { designId ->
                    val route = if (designId != null) "${Routes.AR_SCREEN}?designId=$designId" else Routes.AR_SCREEN
                    navController.navigate(route)
                },
                onLogout = {
                    authViewModel.logout()
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }

        composable(
            route = "${Routes.AR_SCREEN}?designId={designId}",
            arguments = listOf(
                navArgument("designId") {
                    type = NavType.LongType
                    defaultValue = -1L
                }
            )
        ) { backStackEntry ->
            val designId = backStackEntry.arguments?.getLong("designId") ?: -1L
            ARScreen(
                designId = if (designId != -1L) designId else null,
                onLogout = {
                    authViewModel.logout()
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
    }
}
